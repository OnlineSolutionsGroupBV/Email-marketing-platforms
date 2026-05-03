# -*- coding: utf-8 -*-
import json
import requests
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Send a test email via HTTP to the local /api/send-email/ endpoint.'

    def handle(self, *args, **options):
        url = 'http://webmailer.auto-tweedehands.com/api/send-email/'  # lokaal endpoint

        text_body = u"UTF-8 test: humanit\u00e9, foto's, tweedehands bedrijfswagens.\nAfmelden: https://sendgrid.auto-tweedehands.com/mailing/unsubscribe/one-click/?id=test"
        html_body = u"<p>UTF-8 test: humanit\u00e9, foto's, tweedehands bedrijfswagens.</p><p>Afmelden: <a href=\"https://sendgrid.auto-tweedehands.com/mailing/unsubscribe/one-click/?id=test\">uitschrijven</a></p>"

        payload = {
            "client_id": "test-http-command",
            "from_email": "contact@autoverkopen.email",
            "to_email": "test-9op06vehp@srv1.mail-tester.com",  # vervang met geldig testadres
            "subject": "UTF-8 DKIM test via webmailer",
            "text_body": text_body,
            "html_body": html_body,
            "unsubscribe_email": "contact@autoverkopen.email",
            "unsubscribe_url": "https://sendgrid.auto-tweedehands.com/mailing/unsubscribe/autoverkopen-email/?id=test",
            "one_click_unsubscribe_url": "https://sendgrid.auto-tweedehands.com/mailing/unsubscribe/one-click/?id=test"
        }

        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
            if response.status_code == 200:
                self.stdout.write(('Test email sent via HTTP: %s' % response.json()))
            else:
                self.stderr.write(('Failed with status %s: %s' % (response.status_code, response.text)))
        except Exception as e:
            self.stderr.write(('Request error: %s' % e))
