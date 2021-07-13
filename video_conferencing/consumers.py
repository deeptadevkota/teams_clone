from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from .models import *


# Class to handle the websocket connection of Video conferencing room

class ConnectConsumer(WebsocketConsumer):
    http_user = True
    # obtained the team_id and username
    # initiates the websocket connection

    def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['team_id']
        self.user = self.scope["user"]
        self.user_id = self.user.username
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
        # gets the old chat messages from the databaseforms a list of messages,

        chats = Chat.objects.filter(team_id=int(self.room_id))
        chat_msg = []
        for chat in chats:
            chat_msg.append(chat.message)

        #  and passes the list to the browser
        self.send(text_data=json.dumps({
            'obj': {'type': 'msg', 'message': chat_msg, 'user_name': 'test'}
        }))

    # closes the websocket connection and sends the left message to the browser
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

    # Receives message from WebSocket and sends it to the browser
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
        # checks if the message type is msg if yes then saves the message
        if type == 'msg':
            chat = Chat()
            chat.team_id = int(self.room_id)
            chat.message = text_data_json['message'][0]
            chat.save()

    # function to send the message to the browser
    def connection_message(self, event):
        self.send(text_data=json.dumps({
            'obj': event['obj'],
        }))


# Class to handle the websocket connection of the Dashboard chat feature

class ChatConsumer(WebsocketConsumer):
    # inittates the websocker connection
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['team_id']
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
        }))

    # function to disconnect the websocket connection
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_name,
            self.channel_name
        )

    # receives message from the websocket and sends it to the browser
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        async_to_sync(self.channel_layer.group_send)(
            self.room_name,
            {
                'type': 'chat_message',
                'message': [message]
            }
        )
        # saves the chat messages
        chat = Chat()
        chat.team_id = int(self.room_name)
        chat.message = message
        chat.save()
    # sends message to the web browser

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'message': message,
            'type': "chat_message"
        }))
