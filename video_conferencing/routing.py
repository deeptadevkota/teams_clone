from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/(?P<room_id>\w+)/(?P<user_id>\w+)/$',
            consumers.ConnectConsumer),
    re_path(r'ws/dashboard/(?P<team_id>\w+)/(?P<name>\w+)/$',
            consumers.ChatConsumer),
]
