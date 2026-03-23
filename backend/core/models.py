from django.db import models
from django.conf import settings


class ChatRoom(models.Model):
    COURSE = 'course'
    DIRECT = 'direct'
    GENERAL = 'general'
    ROOM_TYPES = [(COURSE, 'Course'), (DIRECT, 'Direct'), (GENERAL, 'General')]

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    room_type = models.CharField(
        max_length=20, choices=ROOM_TYPES, default=GENERAL)
    course = models.ForeignKey(
        'courses.Course', on_delete=models.CASCADE, null=True, blank=True, related_name='chat_rooms'
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='chat_rooms', blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_rooms'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_rooms'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Message(models.Model):
    room = models.ForeignKey(
        ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    attachment = models.FileField(
        upload_to='chat_attachments/', null=True, blank=True)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'messages'
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.room.name}] {self.sender.email}: {self.content[:60]}"


class Notification(models.Model):
    INFO = 'info'
    SUCCESS = 'success'
    WARNING = 'warning'
    ERROR = 'error'
    TYPE_CHOICES = [(INFO, 'Info'), (SUCCESS, 'Success'),
                    (WARNING, 'Warning'), (ERROR, 'Error')]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20, choices=TYPE_CHOICES, default=INFO)
    is_read = models.BooleanField(default=False)
    action_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.title}"
