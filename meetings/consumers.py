import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Meeting, Message
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f"chat_{self.room_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        user_email = data.get('sender')

        # حفظ الرسالة في قاعدة البيانات
        try:
            user = await User.objects.aget(email=user_email)
            meeting = await Meeting.objects.aget(room_id=self.room_id)
            await Message.objects.acreate(meeting=meeting, user=user, content=message)
        except Exception as e:
            print(f"Error saving message: {e}")

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': user_email,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
        }))
