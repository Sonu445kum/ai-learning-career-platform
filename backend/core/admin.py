from django.contrib import admin
from .models import ChatRoom, Message, Notification


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'room_type', 'is_active', 'created_at']
    list_filter = ['room_type', 'is_active']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['members']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['room', 'sender',
                    'content_preview', 'is_deleted', 'created_at']
    list_filter = ['is_deleted', 'is_edited']
    search_fields = ['sender__email', 'content']
    readonly_fields = ['created_at', 'updated_at']

    def content_preview(self, obj):
        return obj.content[:80]
    content_preview.short_description = 'Content'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title',
                    'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']
    search_fields = ['user__email', 'title']
