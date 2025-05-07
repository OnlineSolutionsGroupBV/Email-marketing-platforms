import json
import requests
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Send a test email via HTTP to the local /api/send-email/ endpoint.'

    def handle(self, *args, **options):
        url = 'http://webmailer.auto-tweedehands.com/api/send-email/'  # lokaal endpoint

        payload = {
            "client_id": "test-http-command",
            "from_email": "info@auto-tweedehands.com",
            "to_email": "test-9op06vehp@srv1.mail-tester.com",  # vervang met geldig testadres
            "subject": "Test Email from HTTP Command",
            "text_body": "Hello, this is a test email sent via HTTP POST from testmail command."
        }

        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            if response.status_code == 200:
                self.stdout.write(('Test email sent via HTTP: %s' % response.json()))
            else:
                self.stderr.write(('Failed with status %s: %s' % (response.status_code, response.text)))
        except Exception as e:
            self.stderr.write(('Request error: %s' % e))

