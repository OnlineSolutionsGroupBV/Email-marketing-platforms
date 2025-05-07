from django.db import models

class EmailMessage(models.Model):
    client_id = models.CharField(max_length=100)
    from_email = models.EmailField()
    to_email = models.EmailField()
    subject = models.CharField(max_length=255)
    text_body = models.TextField(blank=True, null=True)
    html_body = models.TextField(blank=True, null=True)
    unsubscribe_url = models.URLField(blank=True, null=True)

    STATUS_CHOICES = (
        ('queued', 'Queued'),
        ('sent', 'Sent'),
        ('bounced', 'Bounced'),
        ('deferred', 'Deferred'),
        ('failed', 'Failed'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='queued')
    log = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"%s -> %s (%s)" % (self.from_email, self.to_email, self.status)

