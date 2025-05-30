from django.core.management.base import BaseCommand
from maillogger.models import SuppressedEmail

class Command(BaseCommand):
    help = 'Reset all SuppressedEmail statuses to "pending"'

    def handle(self, *args, **options):
        updated_count = SuppressedEmail.objects.update(status='pending')
        self.stdout.write("Updated {} suppressed emails to status 'pending'.".format(updated_count))

