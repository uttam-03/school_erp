"""WebSocket consumer for real-time notifications."""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Notification


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close()
            return
        self.user = self.scope['user']
        self.group_name = f'notifications_{self.user.id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        # Send unread count on connect
        count = await self.get_unread_count()
        await self.send(text_data=json.dumps({'type': 'unread_count', 'count': count}))

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('action') == 'mark_read':
            notif_id = data.get('notification_id')
            if notif_id:
                await self.mark_notification_read(notif_id)
                count = await self.get_unread_count()
                await self.send(text_data=json.dumps({'type': 'unread_count', 'count': count}))

    async def notification_message(self, event):
        """Handle notification pushed from server."""
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'title': event['title'],
            'message': event['message'],
            'notification_type': event['notification_type'],
            'link': event.get('link', ''),
            'created_at': event['created_at'],
        }))

    @database_sync_to_async
    def get_unread_count(self):
        return Notification.objects.filter(recipient=self.user, is_read=False).count()

    @database_sync_to_async
    def mark_notification_read(self, notif_id):
        Notification.objects.filter(id=notif_id, recipient=self.user).update(is_read=True)
