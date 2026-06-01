from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError

from maillogger.models import EmailLog


class Command(BaseCommand):
    help = "Preview or delete EmailLog rows for a recipient, optionally filtered by bounce type/status."

    def add_arguments(self, parser):
        parser.add_argument("recipient", help="Exact recipient email address to match.")
        parser.add_argument(
            "--bounce-type",
            default=None,
            help="Optional bounce_type filter, for example hard or soft.",
        )
        parser.add_argument(
            "--status",
            default=None,
            help="Optional status filter, for example bounced or deferred.",
        )
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Actually delete matching rows. Without this flag only a preview is printed.",
        )
        parser.add_argument(
            "--limit-preview",
            type=int,
            default=50,
            help="Maximum matching rows to print in preview.",
        )

    def handle(self, *args, **options):
        recipient = options["recipient"].strip().lower()
        if not recipient or "@" not in recipient:
            raise CommandError("Recipient must be a valid email address.")

        qs = EmailLog.objects.filter(recipient__iexact=recipient)
        if options["bounce_type"]:
            qs = qs.filter(bounce_type=options["bounce_type"])
        if options["status"]:
            qs = qs.filter(status=options["status"])

        count = qs.count()
        self.stdout.write("recipient=%s" % recipient)
        self.stdout.write("bounce_type=%s" % (options["bounce_type"] or "any"))
        self.stdout.write("status=%s" % (options["status"] or "any"))
        self.stdout.write("matched=%d" % count)

        preview_limit = max(int(options["limit_preview"]), 0)
        if preview_limit:
            for row in qs.order_by("-logged_at").values(
                "id",
                "recipient",
                "status",
                "bounce_type",
                "reason",
                "logged_at",
            )[:preview_limit]:
                self.stdout.write(
                    "id=%s recipient=%s status=%s bounce_type=%s logged_at=%s reason=%s"
                    % (
                        row["id"],
                        row["recipient"],
                        row["status"],
                        row["bounce_type"],
                        row["logged_at"],
                        (row["reason"] or "")[:180],
                    )
                )

        if not options["delete"]:
            self.stdout.write("Preview only. Re-run with --delete to remove these rows.")
            return

        deleted = qs.delete()
        self.stdout.write("deleted=%s" % (deleted,))
