import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async  
from datetime import timedelta
from django.utils import timezone

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'main_chatroom'
        self.room_group_name = f'chat_{self.room_name}'

        if self.scope['user'].is_anonymous:
            await self.close()
        else:      
            await self.load_chat_history()
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name,
                
            )

            await self.accept()

    @database_sync_to_async
    def load_chat_history(self):
        from .models import ChatMessage 
        current_time = timezone.now()
        twenty_four_hours_ago = current_time - timedelta(hours=24)
        chat_messages = ChatMessage.objects.filter(timestamp__gte=twenty_four_hours_ago).order_by('timestamp')

        messages = []  
        for message in chat_messages:
            messages.append({
                'message': message.content,
                'username': message.sender,
            })

        self.send(text_data=json.dumps({
            'command': 'load_history',
            'messages': messages,
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name


            
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = self.scope['user'].username



        await self.save_chat_message(username, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
            }
        )

    @database_sync_to_async
    def save_chat_message(self, username, message):
        from .models import ChatMessage 
        ChatMessage.objects.create(sender=username, content=message)

    
    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
        }))