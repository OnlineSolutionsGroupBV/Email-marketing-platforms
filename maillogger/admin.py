from django.contrib import admin
from .models import EmailLog, SuppressedEmail

class SuppressedEmailAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'status', 'added_at', 'updated_at')
    search_fields = ('recipient', 'reason')
    list_filter = ('status', 'added_at')
    ordering = ('-added_at',)



def mark_as_hard_bounce(modeladmin, request, queryset):
    updated = queryset.update(status='bounced', bounce_type='hard')
    modeladmin.message_user(request, "%d emails marked as hard bounce." % updated)

mark_as_hard_bounce.short_description = "Mark selected deferred emails as hard bounced"

class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'status', 'reason', 'logged_at')
    search_fields = ('recipient', 'status', 'reason')
    list_filter = ('status', 'logged_at', 'bounce_type')
    actions = [mark_as_hard_bounce]

admin.site.register(EmailLog, EmailLogAdmin)
admin.site.register(SuppressedEmail, SuppressedEmailAdmin)
