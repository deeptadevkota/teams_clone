from django.urls import path
from .views import *

urlpatterns = [
    path('<str:room_id>/<str:user_name>/', home_page, name="home_page"),
    path('login/', login_page, name="login_page"),
    path('register/', register_page, name="register_page"),
    path('dashboard/', dashboard_page, name="dashboard_page"),

 ]
