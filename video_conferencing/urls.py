from django.urls import path
from .views import *

urlpatterns = [

    path('login/', login_page, name="login_page"),
    path('register/', register_page, name="register_page"),
    path('logout/', logout_page, name="logout_page"),
    path('dashboard/<str:team_id>/', dashboard_page, name="dashboard_page"),
    path('team_form/', team_form_page, name="team_form_page"),
    path('add_members/<str:team_id>/', add_members_page, name="add_members_page"),
    path('<str:room_id>/<str:user_name>/', home_page, name="home_page"),

]
