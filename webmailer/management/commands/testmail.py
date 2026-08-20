# -*- coding: utf-8 -*-
import json
import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Send a test email via HTTP to the local /api/send-email/ endpoint.'

    def handle(self, *args, **options):
        required_settings = (
            'WEBMAILER_TEST_API_URL',
            'WEBMAILER_TEST_TO_EMAIL',
            'WEBMAILER_TEST_UNSUBSCRIBE_URL',
            'WEBMAILER_TEST_ONE_CLICK_UNSUBSCRIBE_URL',
        )
        missing = [name for name in required_settings if not getattr(settings, name, None)]
        if missing:
            raise CommandError(
                'Missing required setting(s): %s' % ', '.join(missing)
            )

        url = settings.WEBMAILER_TEST_API_URL
        from_email = getattr(settings, 'WEBMAILER_TEST_FROM_EMAIL', settings.DEFAULT_FROM_EMAIL)
        unsubscribe_email = getattr(settings, 'WEBMAILER_TEST_UNSUBSCRIBE_EMAIL', from_email)
        unsubscribe_url = settings.WEBMAILER_TEST_UNSUBSCRIBE_URL
        one_click_url = settings.WEBMAILER_TEST_ONE_CLICK_UNSUBSCRIBE_URL

        text_body = (
            u"UTF-8 test: humanit\u00e9, foto's, tweedehands bedrijfswagens.\n"
            u"Afmelden: %s" % unsubscribe_url
        )
        html_body = (
            u"<p>UTF-8 test: humanit\u00e9, foto's, tweedehands bedrijfswagens.</p>"
            u"<p>Afmelden: <a href=\"%s\">uitschrijven</a></p>" % unsubscribe_url
        )

        payload = {
            "client_id": "test-http-command",
            "from_email": from_email,
            "to_email": settings.WEBMAILER_TEST_TO_EMAIL,
            "subject": getattr(settings, 'WEBMAILER_TEST_SUBJECT', 'UTF-8 DKIM test via webmailer'),
            "text_body": text_body,
            "html_body": html_body,
            "unsubscribe_email": unsubscribe_email,
            "unsubscribe_url": unsubscribe_url,
            "one_click_unsubscribe_url": one_click_url,
        }

        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                timeout=getattr(settings, 'WEBMAILER_TEST_TIMEOUT', 30),
            )
        except Exception as e:
            raise CommandError('Request error: %s' % e)

        try:
            response_data = response.json()
        except ValueError:
            raise CommandError(
                'Non-JSON response (HTTP %s): %s' %
                (response.status_code, response.text)
            )

        if response.status_code != 200 or response_data.get('status') != 'sent':
            raise CommandError(
                'Test email failed (HTTP %s): %s' %
                (response.status_code, response_data)
            )

        self.stdout.write('Test email sent via HTTP: %s' % response_data)
