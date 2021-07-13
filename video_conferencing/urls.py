''' 
URL configuration for the app
Class-based views
     1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
'''

from django.urls import path
from .views import *

urlpatterns = [
    path('', login_page, name="login_page"),
    path('register/', register_page, name="register_page"),
    path('logout/', logout_page, name="logout_page"),
    path('dashboard/<str:team_id>/', dashboard_page, name="dashboard_page"),
    path('team_form/', team_form_page, name="team_form_page"),
    path('add_members/<str:team_id>/', add_members_page, name="add_members_page"),
    path('<str:team_id>/', video_page, name="video_page"),
]
