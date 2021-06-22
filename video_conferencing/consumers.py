from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json


class ConnectConsumer(WebsocketConsumer):
    def connect(self):
        # print("HERE")
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        async_to_sync(self.channel_layer.group_send)(
            self.room_id,
            {
                'type': 'connection_message',
                'obj': {'name':self.user_id,'type':'joined'}
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
                'obj': {'name':self.user_id,'type':'left'}
            }
        )
        async_to_sync(self.channel_layer.group_discard)(
            self.room_id,
            self.channel_name
        )
# made changes here

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
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
