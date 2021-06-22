from django.shortcuts import render
from .models import *

# Create your views here.


def home_page(request, room_id, user_name):
    return render(request, 'video_conferencing/home.html', {'room_id': room_id, 'user_name': user_name})


def login_page(request):
    return render(request, 'video_conferencing/login.html', {})


def register_page(request):
    return render(request, 'video_conferencing/register.html', {})


def dashboard_page(request):
    return render(request, 'video_conferencing/dashboard.html', {})
