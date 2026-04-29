from __future__ import unicode_literals

from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from maillogger.models import EmailLog
from maillogger.notifier import notify_contact_status
from maillogger.provider_utils import detect_provider

import json


@csrf_exempt
def email_log_api(request):
    if request.method != 'POST':
        return HttpResponseBadRequest("Only POST allowed")

    expected_key = getattr(settings, 'EMAIL_LOG_INGEST_KEY', None)
    provided_key = request.META.get('HTTP_X_EMAIL_LOG_KEY') or request.POST.get('key')
    if expected_key and provided_key != expected_key:
        return HttpResponseForbidden("Invalid key")

    if request.META.get('CONTENT_TYPE', '').startswith('application/json'):
        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        data = request.POST

    recipient = (data.get('recipient') or data.get('email') or '').strip().lower()
    if not recipient:
        return HttpResponseBadRequest("Missing recipient")

    use_mx = str(data.get('use_mx', '')).lower() in ('1', 'true', 'yes')
    provider, domain, mx_domain = detect_provider(recipient, use_mx=use_mx)
    provider = data.get('provider') or provider
    mx_domain = data.get('mx_domain') or mx_domain

    email_log = EmailLog.objects.create(
        recipient=recipient,
        sender=data.get('sender') or None,
        status=(data.get('status') or 'unknown').strip().lower(),
        reason=data.get('reason') or data.get('status_message') or None,
        bounce_type=data.get('bounce_type') or None,
        message_id=data.get('message_id') or None,
        recipient_domain=domain,
        provider=provider,
        mx_domain=mx_domain,
        source_server=data.get('source_server') or None,
        raw_line=data.get('raw') or None,
    )

    if str(data.get('notify_contact', '')).lower() in ('1', 'true', 'yes'):
        notify_contact_status(email_log)

    return JsonResponse({'status': 'ok', 'id': email_log.id})
