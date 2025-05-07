
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.conf import settings
from django.utils import timezone
from .models import EmailMessage
from .forms import EmailForm
from django.core.mail import EmailMultiAlternatives
import json


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


@csrf_exempt
def send_email_api(request):
    if request.method != 'POST':
        return HttpResponseBadRequest("Only POST allowed")

    ip = get_client_ip(request)
    allowed_ips = getattr(settings, 'ALLOWED_SENDER_IPS', [])
    if ip not in allowed_ips:
        return HttpResponseForbidden("Unauthorized IP: %s" % ip)

    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    form = EmailForm(data)
    if not form.is_valid():
        return JsonResponse({'error': form.errors}, status=400)

    cleaned = form.cleaned_data

    email = EmailMessage.objects.create(
        client_id=cleaned['client_id'],
        from_email=cleaned['from_email'],
        to_email=cleaned['to_email'],
        subject=cleaned['subject'],
        text_body=cleaned.get('text_body'),
        html_body=cleaned.get('html_body'),
        unsubscribe_url=cleaned.get('unsubscribe_url'),
        status='queued',
    )

    try:
        msg = EmailMultiAlternatives(
            subject=email.subject,
            body=email.text_body or '',
            from_email=email.from_email,
            to=[email.to_email]
        )
        if email.html_body:
            msg.attach_alternative(email.html_body, "text/html")

        # List-Unsubscribe
        if email.unsubscribe_url:
            unsubscribe = "<%s>" % email.unsubscribe_url
        else:
            unsubscribe = "<mailto:%s>" % email.from_email
        msg.extra_headers = {'List-Unsubscribe': unsubscribe}

        msg.send()
        email.status = 'sent'
        email.sent_at = timezone.now()
    except Exception as e:
        email.status = 'failed'
        email.log = str(e)
    email.save()

    return JsonResponse({'status': email.status, 'id': email.id})

