from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json

from django.contrib import messages
from .models import *


class ConnectConsumer(WebsocketConsumer):
    def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        async_to_sync(self.channel_layer.group_send)(
            self.room_id,
            {
                'type': 'connection_message',
                'obj': {'name': self.user_id, 'type': 'joined'}
            }
        )
        async_to_sync(self.channel_layer.group_add)(
            self.room_id,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_send)(
            self.room_id,
            {
                'type': 'connection_message',
                'obj': {'name': self.user_id, 'type': 'left'}
            }
        )
        async_to_sync(self.channel_layer.group_discard)(
            self.room_id,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print(text_data_json)
        async_to_sync(self.channel_layer.group_send)(
            self.room_id,
            {
                'type': 'connection_message',
                'obj': text_data_json
            }
        )

    def connection_message(self, event):
        self.send(text_data=json.dumps({
            'obj': event['obj'],
        }))


# another view class


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['team_id']

        async_to_sync(self.channel_layer.group_add)(
            self.room_name,
            self.channel_name
        )
        self.accept()

        # here is exactly where you extract the stored chats from the data base and send it as a message
        chats = Chat.objects.filter(team_id=int(self.room_name))
        chat_msg = []
        for chat in chats:
            chat_msg.append(chat.message)
        async_to_sync(self.channel_layer.group_send)(
            self.room_name,
            {
                'type': 'chat_message',
                'message': chat_msg
            }
        )

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_name,
            {
                'type': 'chat_message',
                'message': [message]
            }
        )

        chat = Chat()
        chat.team_id = int(self.room_name)
        chat.message = message
        chat.save()

    # Receive message from room group

    def chat_message(self, event):
        message = event['message']
        print("hi")
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'type': "chat_message"
        }))
