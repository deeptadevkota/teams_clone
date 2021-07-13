import os
import django
from channels.routing import get_default_application

#setting up the asgi application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WebRtc.settings')
django.setup()
application = get_default_application()
