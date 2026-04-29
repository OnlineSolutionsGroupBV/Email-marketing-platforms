from __future__ import unicode_literals

from django.conf import settings
from django.utils import timezone

import requests


def notify_contact_status(email_log):
    url = getattr(settings, 'CONTACT_STATUS_UPDATE_URL', None)
    key = getattr(settings, 'CONTACT_PROVIDER_UPDATE_KEY', None)
    enabled = getattr(settings, 'CONTACT_STATUS_UPDATE_ENABLED', False)
    timeout = getattr(settings, 'CONTACT_STATUS_UPDATE_TIMEOUT', 10)

    if not enabled or not url or not key:
        return False

    payload = {
        'email': email_log.recipient,
        'provider': email_log.provider or '',
        'provider_source': 'maillogger',
        'mx_domain': email_log.mx_domain or '',
        'status': email_log.status,
        'status_code': '',
        'status_message': email_log.reason or '',
        'bounce_type': email_log.bounce_type or '',
        'raw': email_log.raw_line or '',
    }

    response = requests.post(
        url,
        data=payload,
        headers={'X-Contact-Provider-Key': key},
        timeout=timeout,
    )
    email_log.notified_at = timezone.now()
    email_log.notify_status = str(response.status_code)
    email_log.save()
    return response.status_code >= 200 and response.status_code < 300
