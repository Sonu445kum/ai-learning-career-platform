import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time chat."""

    async def connect(self):
        self.room_slug = self.scope['url_route']['kwargs']['room_slug']
        self.room_group_name = f'chat_{self.room_slug}'
        self.user = self.scope.get('user')

        if not self.user or not self.user.is_authenticated:
            await self.close()
            return

        # Check room access
        room = await self.get_room(self.room_slug)
        if not room:
            await self.close()
            return
        self.room = room

        # Join channel group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Send join notification
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_join',
                'user_id': self.user.id,
                'username': self.user.get_full_name() or self.user.email,
            }
        )

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_leave',
                    'user_id': self.user.id,
                    'username': self.user.get_full_name() or self.user.email,
                }
            )
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'chat_message')

            if message_type == 'chat_message':
                content = data.get('content', '').strip()
                if not content:
                    return

                # Persist message to DB
                msg = await self.save_message(content)

                # Broadcast to room
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'id': msg.id,
                        'content': content,
                        'sender_id': self.user.id,
                        'sender_name': self.user.get_full_name() or self.user.email,
                        'sender_avatar': await self.get_avatar(),
                        'created_at': msg.created_at.isoformat(),
                    }
                )
            elif message_type == 'typing':
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'typing_indicator',
                        'user_id': self.user.id,
                        'username': self.user.get_full_name(),
                        'is_typing': data.get('is_typing', False),
                    }
                )
        except (json.JSONDecodeError, KeyError):
            pass

    # ── Event handlers ──────────────────────────────────────────────────────

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'id': event['id'],
            'content': event['content'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'sender_avatar': event.get('sender_avatar'),
            'created_at': event['created_at'],
        }))

    async def user_join(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_join',
            'user_id': event['user_id'],
            'username': event['username'],
        }))

    async def user_leave(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_leave',
            'user_id': event['user_id'],
            'username': event['username'],
        }))

    async def typing_indicator(self, event):
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user_id': event['user_id'],
                'username': event['username'],
                'is_typing': event['is_typing'],
            }))

    # ── Database helpers ─────────────────────────────────────────────────────

    @database_sync_to_async
    def get_room(self, slug):
        try:
            return ChatRoom.objects.get(slug=slug, is_active=True)
        except ChatRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, content):
        return Message.objects.create(
            room=self.room,
            sender=self.user,
            content=content,
        )

    @database_sync_to_async
    def get_avatar(self):
        if self.user.avatar:
            return self.user.avatar.url
        return None
