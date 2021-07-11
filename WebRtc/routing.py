from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path
from video_conferencing import consumers


application = ProtocolTypeRouter({
    # Empty for now (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            [
                re_path(r'ws/dashboard/(?P<team_id>\w+)/$',
                        consumers.ChatConsumer),
                re_path(r'ws/(?P<room_id>\w+)/$',
                        consumers.ConnectConsumer)
            ]
        )
    ),
})
