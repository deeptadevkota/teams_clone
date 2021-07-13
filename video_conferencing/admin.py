# importing the dajngo admin and the models

from django.contrib import admin
from .models import *

# Registering the models to appear in the super user's page

admin.site.register(Team)
admin.site.register(User_Team)
admin.site.register(Chat)
