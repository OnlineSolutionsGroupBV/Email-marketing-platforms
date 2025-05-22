from django.contrib import admin
from .models import EmailLog

class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'status', 'reason', 'logged_at')
    search_fields = ('recipient', 'status', 'reason')
    list_filter = ('status', 'logged_at', 'bounce_type')

admin.site.register(EmailLog, EmailLogAdmin)

