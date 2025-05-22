from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from maillogger.models import EmailLog

class Command(BaseCommand):
    help = 'Classifies bounced emails as hard or soft'

    def handle(self, *args, **options):
        bounces = EmailLog.objects.filter(status='bounced').filter(reason__icontains='curently over quota') 
        # bounce_type__isnull=True

        count = 0

        for log in bounces:
            bounce_type = log.classify_bounce()
            if bounce_type:
                log.bounce_type = bounce_type
                log.save()
                count += 1

        self.stdout.write("Classified %d bounced emails" % count)

