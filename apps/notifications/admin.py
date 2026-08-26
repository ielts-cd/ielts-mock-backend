from django.contrib import admin
from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender_role', 'sender_name', 'recipient_role', 'recipient_name', 'status', 'created_at')
    list_filter = ('sender_role', 'recipient_role', 'status')
    search_fields = ('sender_name', 'recipient_name', 'message')
