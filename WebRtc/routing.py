from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import video_conferencing.routing

application = ProtocolTypeRouter({
     # Empty for now (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            video_conferencing.routing.websocket_urlpatterns
        )
    ),
})
