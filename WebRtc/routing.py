from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path
from video_conferencing import consumers

# define the route for the websocket URL
# considers the URL path pattern
application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            [
                re_path(r'ws/dashboard/(?P<team_id>\w+)/$',
                        consumers.ChatConsumer),
                re_path(r'ws/(?P<team_id>\w+)/$',
                        consumers.ConnectConsumer)
            ]
        )
    ),
})
