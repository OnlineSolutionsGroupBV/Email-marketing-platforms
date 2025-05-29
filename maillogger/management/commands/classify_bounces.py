# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from maillogger.models import EmailLog

class Command(BaseCommand):
    help = 'Classifies bounced emails as hard or soft'

    def handle(self, *args, **options):
        #bounces = EmailLog.objects.filter
        #filter(status='bounced').filter(reason__icontains='curently over quota') 
        # bounce_type__isnull=True
        
        # Filter only bounced and deferred emails with no bounce_type yet
        bounces = EmailLog.objects.filter(status__in=['bounced', 'deferred'])
            
        total = 0
        hard = 0
        soft = 0
    
        for log in bounces:
            bounce_type = log.classify_bounce()

            log.bounce_type = bounce_type

            # Promote deferred to bounced if it's a hard bounce
            if bounce_type == 'hard' and log.status == 'deferred':
                log.status = 'bounced'
                hard += 1
            elif bounce_type == 'soft':
                soft += 1

            log.save()
            total += 1

        self.stdout.write("✅ Reclassified %d email logs." % total)
        self.stdout.write("   Hard bounces: %d" % hard)
        self.stdout.write("   Soft bounces: %d" % soft)
