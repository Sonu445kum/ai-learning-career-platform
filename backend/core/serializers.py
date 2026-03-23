from rest_framework import serializers
from .models import ChatRoom, Message, Notification
from accounts.serializers import UserSerializer


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'content',
                  'attachment', 'is_edited', 'created_at']
        read_only_fields = ['id', 'sender', 'is_edited', 'created_at']


class ChatRoomSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'slug', 'room_type', 'course', 'is_active',
                  'created_at', 'last_message', 'member_count']
        read_only_fields = ['id', 'slug', 'created_at']

    def get_last_message(self, obj):
        last = obj.messages.filter(is_deleted=False).last()
        if last:
            return {'content': last.content[:100], 'sender': last.sender.get_full_name(), 'created_at': last.created_at}
        return None

    def get_member_count(self, obj):
        return obj.members.count()


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'notification_type',
                  'is_read', 'action_url', 'created_at']
        read_only_fields = ['id', 'created_at']
