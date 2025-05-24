# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import requests
from django.core.management.base import BaseCommand
from maillogger.models import SuppressedEmail

class Command(BaseCommand):
    help = "Send suppressed emails (status=processing) to an unsubscribe URL and mark them as done."

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            required=True,
            help='Unsubscribe API endpoint, e.g., https://example.com/unsubscribe'
        )

    def handle(self, *args, **options):
        unsubscribe_url = options['url']

        # Counts for visibility
        total_all = SuppressedEmail.objects.count()
        total_done = SuppressedEmail.objects.filter(status='done').count()
        total_pending = SuppressedEmail.objects.filter(status='pending').count()
        total_exported = SuppressedEmail.objects.filter(status='exported').count()
        emails_to_process = SuppressedEmail.objects.filter(status='pending')
        total_processing = emails_to_process.count()

        # Print overview
        self.stdout.write("📊 Suppressed Email Overview")
        self.stdout.write("--------------------------------------")
        self.stdout.write("   Total emails:          %d" % total_all)
        self.stdout.write("   Already unsubscribed:  %d (status='done')" % total_done)
        self.stdout.write("   Waiting to process:    %d (status='pending')" % total_pending)
        self.stdout.write("   Exported but not sent: %d (status='exported')" % total_exported)
        self.stdout.write("   Processing now:        %d (status='processing')" % total_processing)
        self.stdout.write("--------------------------------------\n")

        if total_processing == 0:
            self.stdout.write("✅ Nothing to process.")
            return

        success = 0
        failed = 0

        for idx, email in enumerate(emails_to_process, start=1):
            self.stdout.write("🔄 Unsubscribing [%d of %d]: %s" % (idx, total_processing, email.recipient))

            try:
                response = requests.get(unsubscribe_url, params={'email': email.recipient}, timeout=10)

                if response.status_code == 200:
                    email.status = 'done'
                    email.save()
                    success += 1
                    self.stderr.write(response.content)
                else:
                    failed += 1
                    self.stderr.write("   ✖ Failed (%d)\n" % response.status_code)

            except Exception as e:
                failed += 1
                self.stderr.write("   ✖ Error: %s\n" % str(e))

        self.stdout.write("\n✅ Finished Processing")
        self.stdout.write("--------------------------------------")
        self.stdout.write("   Emails processed:  %d" % total_processing)
        self.stdout.write("   Successfully done: %d" % success)
        self.stdout.write("   Failed:            %d" % failed)
        self.stdout.write("--------------------------------------")

