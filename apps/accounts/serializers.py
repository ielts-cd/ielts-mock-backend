from rest_framework import serializers
from .models import Organization, User, SupportTicket
from apps.exams.models import Group

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'org_name', 'ceo_name', 'phone', 'email', 'username', 'password',
                  'telegram_chat_id', 'avatar', 'status', 'created_at', 'updated_at']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['id'] = validated_data.get('id') or f"org_{self.context.get('request').user.id}_{int(datetime.now().timestamp())}"
        instance = Organization(**validated_data)
        instance.set_password(validated_data['password'])
        instance.save()
        return instance

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
            del validated_data['password']
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    group_name = serializers.SerializerMethodField()
    group_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'organization', 'name', 'username', 'password', 'phone',
                  'role', 'telegram_chat_id', 'avatar', 'status', 'group', 'group_name',
                  'group_id', 'created_at', 'updated_at']
        extra_kwargs = {'password': {'write_only': True}}

    def get_group_name(self, obj):
        if obj.group:
            return obj.group.name
        return None

    def get_group_id(self, obj):
        if obj.group:
            return obj.group.id
        return None

    def create(self, validated_data):
        validated_data['id'] = f"usr_{int(datetime.now().timestamp())}_{self.context.get('request').user.id}"
        instance = User(**validated_data)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.save()
        return instance

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
            del validated_data['password']
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class SupportTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTicket
        fields = ['id', 'organization', 'user', 'user_name', 'user_role', 'org_name',
                  'message', 'seen', 'created_at']
        read_only_fields = ['id', 'created_at']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    role = serializers.CharField(required=False)


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField(min_length=4)