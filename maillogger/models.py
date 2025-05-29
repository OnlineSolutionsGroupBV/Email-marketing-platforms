from __future__ import unicode_literals
from django.db import models
import re

class EmailLog(models.Model):
    recipient = models.EmailField()
    sender = models.EmailField(blank=True, null=True)
    status = models.CharField(max_length=20)  # sent, bounced, etc.
    reason = models.TextField(blank=True, null=True)
    bounce_type = models.CharField(max_length=10, blank=True, null=True)  # hard, soft
    message_id = models.CharField(max_length=255, blank=True, null=True)
    logged_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.status in ['bounced', 'deferred'] and not self.bounce_type:
            self.bounce_type = self.classify_bounce()
            # If it is deferred, but it turns out to be a hard bounce:
            if self.status == 'deferred' and self.bounce_type == 'hard':
                self.status = 'bounced' 
        super(EmailLog, self).save(*args, **kwargs)


    def classify_bounce(self):
        hard_bounce_patterns = (
            r"user unknown|mailbox not found|no such user|"
            r"mailbox full|does not exist|no such mailbox|OverQuotaTemp|unable to verify user|"
            r"no such recipient here|name service error|Host not found|"
            r"no mailbox|mailbox is disabled|quota exceeded|"
            r"mailbox might be disabled|no such domain|"
            r"unknown recipient|recipient unknown|currently over quota|"
            r"no mail-enabled subscriptions|out of storage|over quota"
        )

        if re.search(hard_bounce_patterns, self.reason or '', re.IGNORECASE):
            return 'hard'
        return 'soft'


    def __unicode__(self):
        return u"%s - %s" % (self.recipient, self.status)


class SuppressedEmail(models.Model):
    recipient = models.EmailField(unique=True)
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, default='pending')  # pending, done, exported
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return self.recipient


