from django.contrib import admin
from .models import EmailMessage


class EmailMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_id', 'from_email', 'to_email', 'subject', 'status', 'sent_at', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('from_email', 'to_email', 'subject', 'client_id')
    readonly_fields = ('log', 'sent_at', 'created_at')

admin.site.register(EmailMessage, EmailMessageAdmin)

