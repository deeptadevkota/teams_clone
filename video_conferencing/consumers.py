from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from django.contrib import messages
from django.http import request
from .models import *
# from channels.auth import channel_session_user, channel_session_user_from_http


class ConnectConsumer(WebsocketConsumer):
    http_user = True
    def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        # self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.user = self.scope["user"]
        self.user_id = self.user.username
        print(self.user.username)
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
        chats = Chat.objects.filter(team_id=int(self.room_id))
        chat_msg = []
        for chat in chats:
            chat_msg.append(chat.message)
        self.send(text_data=json.dumps({
            'obj': {'type': 'msg', 'message': chat_msg, 'user_name': 'test'}
        }))

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
# made changes here

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        type = text_data_json['type']
        async_to_sync(self.channel_layer.group_send)(
            self.room_id,
            {
                'type': 'connection_message',
                'obj': text_data_json
            }
        )
       # print(text_data_json)
        if type == 'msg':
            chat = Chat()
            chat.team_id = int(self.room_id)
            chat.message = text_data_json['message'][0]
            chat.save()

    def connection_message(self, event):
        self.send(text_data=json.dumps({
            'obj': event['obj'],
        }))


# another view class


class ChatConsumer(WebsocketConsumer):
    http_user = True

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['team_id']
        self.user = self.scope["user"]
        print(self.user)
        async_to_sync(self.channel_layer.group_add)(
            self.room_name,
            self.channel_name
        )
        self.accept()

        chats = Chat.objects.filter(team_id=int(self.room_name))
        chat_msg = []
        for chat in chats:
            chat_msg.append(chat.message)
        self.send(text_data=json.dumps({
            'message': chat_msg,
            'type': "old_msg",
            'user_name': 'test'
        }))

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
        type = text_data_json['type']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_name,
            {
                'type': 'chat_message',
                'message': [message]
            }
        )
        print(text_data_json)
        chat = Chat()
        chat.team_id = int(self.room_name)
        chat.message = message
        chat.save()

    # Receive message from room group

    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'type': "chat_message"
        }))
