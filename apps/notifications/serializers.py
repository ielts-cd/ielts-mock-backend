from rest_framework import serializers
from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    """
    Faqat o'qish uchun (read-only) — yozuvlar MessageViewSet.send() ichida
    to'g'ridan-to'g'ri (fan-out qilib, bir nechta qator sifatida) yaratiladi,
    shuning uchun alohida create()/update() shart emas.
    """
    class Meta:
        model = Message
        fields = [
            'id', 'sender_role', 'sender_id', 'sender_name',
            'recipient_role', 'recipient_id', 'recipient_name',
            'organization', 'message', 'status', 'created_at', 'responded_at',
        ]
        read_only_fields = fields
