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
        if self.status == 'bounced' and not self.bounce_type:
            self.bounce_type = self.classify_bounce()
        super(EmailLog, self).save(*args, **kwargs)

    def classify_bounce(self):
        if self.status == 'bounced' :
            if re.search(r"user unknown|mailbox not found|no such user|mailbox full|does not exist|No such mailbox|No such recipient here|Name service error|no mailbox|mailbox is disabled|Mailbox is full|Quota exceeded|Mailbox might be disabled|No such domain|Unknown recipient|Recipient Unknown|curently over quota|no mail-enabled subscriptions", self.reason or '', re.IGNORECASE):
                return 'hard'
            else:
                return 'soft'
        return None

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


