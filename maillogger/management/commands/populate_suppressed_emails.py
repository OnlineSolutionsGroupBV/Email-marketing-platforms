from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from maillogger.models import EmailLog, SuppressedEmail

class Command(BaseCommand):
    help = 'Populate SuppressedEmail table with unique hard-bounced recipients from EmailLog'

    def handle(self, *args, **options):
        hard_bounces = EmailLog.objects.filter(status='bounced', bounce_type='hard')
        added_count = 0
        skipped_count = 0

        for log in hard_bounces:
            obj, created = SuppressedEmail.objects.get_or_create(
                recipient=log.recipient,
                defaults={
                    'reason': log.reason,
                    'status': 'pending'
                }
            )
            if created:
                added_count += 1
            else:
                skipped_count += 1

        self.stdout.write("SuppressedEmail populated.")
        self.stdout.write("Added: %d | Skipped (already exists): %d" % (added_count, skipped_count))

