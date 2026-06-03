# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

import os
import requests

from maillogger.models import EmailLog


DEFAULT_CONTACT_STATUS_UPDATE_TIMEOUT = 10


class Command(BaseCommand):
    help = "Notify the Contact API for bounced EmailLog rows, defaulting to hard bounces."

    def add_arguments(self, parser):
        parser.add_argument(
            "--url",
            default=None,
            help="Contact status API URL. Defaults to CONTACT_STATUS_UPDATE_URL setting/env var.",
        )
        parser.add_argument(
            "--key",
            default=None,
            help="Contact provider update key. Defaults to CONTACT_PROVIDER_UPDATE_KEY setting/env var.",
        )
        parser.add_argument(
            "--status",
            default="bounced",
            help="EmailLog.status filter. Default: bounced.",
        )
        parser.add_argument(
            "--bounce-type",
            default="hard",
            help="EmailLog.bounce_type filter. Default: hard.",
        )
        parser.add_argument(
            "--q",
            default=None,
            help="Optional recipient contains filter, similar to admin search q.",
        )
        parser.add_argument(
            "--recipient",
            default=None,
            help="Optional exact recipient filter.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Maximum rows to process.",
        )
        parser.add_argument(
            "--timeout",
            type=int,
            default=None,
            help="Request timeout seconds. Defaults to CONTACT_STATUS_UPDATE_TIMEOUT or 10.",
        )
        parser.add_argument(
            "--include-notified",
            action="store_true",
            help="Also process rows that already have notified_at set.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print matching rows and payloads without sending HTTP requests.",
        )

    def handle(self, *args, **options):
        url = (
            options["url"]
            or getattr(settings, "CONTACT_STATUS_UPDATE_URL", None)
            or os.environ.get("CONTACT_STATUS_UPDATE_URL")
        )
        key = (
            options["key"]
            or getattr(settings, "CONTACT_PROVIDER_UPDATE_KEY", None)
            or os.environ.get("CONTACT_PROVIDER_UPDATE_KEY")
        )
        timeout = options["timeout"] or getattr(
            settings,
            "CONTACT_STATUS_UPDATE_TIMEOUT",
            DEFAULT_CONTACT_STATUS_UPDATE_TIMEOUT,
        )

        if not options["dry_run"] and not url:
            raise CommandError("Missing --url or CONTACT_STATUS_UPDATE_URL.")
        if not options["dry_run"] and not key:
            raise CommandError("Missing --key or CONTACT_PROVIDER_UPDATE_KEY.")

        qs = EmailLog.objects.all().order_by("id")
        if options["status"]:
            qs = qs.filter(status=options["status"])
        if options["bounce_type"]:
            qs = qs.filter(bounce_type=options["bounce_type"])
        if options["q"]:
            qs = qs.filter(recipient__icontains=options["q"].strip())
        if options["recipient"]:
            qs = qs.filter(recipient__iexact=options["recipient"].strip())
        if not options["include_notified"]:
            qs = qs.filter(notified_at__isnull=True)

        total = qs.count()
        if options["limit"] is not None:
            qs = qs[: max(int(options["limit"]), 0)]

        self.stdout.write("status=%s" % (options["status"] or "any"))
        self.stdout.write("bounce_type=%s" % (options["bounce_type"] or "any"))
        self.stdout.write("q=%s" % (options["q"] or ""))
        self.stdout.write("recipient=%s" % (options["recipient"] or ""))
        self.stdout.write("include_notified=%s" % options["include_notified"])
        self.stdout.write("matched_total=%d" % total)
        self.stdout.write("processing=%d" % qs.count())
        self.stdout.write("dry_run=%s" % options["dry_run"])
        self.stdout.write("url=%s" % (url or ""))

        sent = 0
        failed = 0
        for email_log in qs:
            payload = {
                "email": email_log.recipient,
                "provider": email_log.provider or "",
                "provider_source": "maillogger",
                "mx_domain": email_log.mx_domain or "",
                "status": email_log.status,
                "status_code": "",
                "status_message": email_log.reason or "",
                "bounce_type": email_log.bounce_type or "",
                "raw": email_log.raw_line or "",
            }

            self.stdout.write(
                "id=%s email=%s status=%s bounce_type=%s reason=%s"
                % (
                    email_log.id,
                    email_log.recipient,
                    email_log.status,
                    email_log.bounce_type,
                    (email_log.reason or "")[:180],
                )
            )

            if options["dry_run"]:
                self.stdout.write("payload=%s" % payload)
                continue

            try:
                response = requests.post(
                    url,
                    data=payload,
                    headers={"X-Contact-Provider-Key": key},
                    timeout=timeout,
                )
                email_log.notify_status = str(response.status_code)
                if response.status_code >= 200 and response.status_code < 300:
                    from django.utils import timezone

                    email_log.notified_at = timezone.now()
                    sent += 1
                else:
                    failed += 1
                email_log.save()
                self.stdout.write("response=%s %s" % (response.status_code, response.text[:300]))
            except Exception as exc:
                failed += 1
                email_log.notify_status = "error"
                email_log.save()
                self.stderr.write("error=%s" % exc)

        self.stdout.write("sent=%d failed=%d" % (sent, failed))
