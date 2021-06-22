from django.shortcuts import render
from .models import *
from django.http import HttpResponse
from django.contrib.auth.models import User, auth



def home_page(request, room_id, user_name):
    return render(request, 'video_conferencing/home.html', {'room_id': room_id, 'user_name': user_name})


def login_page(request):
    return render(request, 'video_conferencing/login.html', {})


def register_page(request):
    return render(request, 'video_conferencing/register.html', {})


def dashboard_page(request):
    return render(request, 'video_conferencing/dashboard.html', {})


def register_form_submission(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = User.objects.create_user(
            username=username, password=password, email=email, last_name=last_name, first_name=first_name)
        user.save()
        return render(request, 'video_conferencing/login.html', {})

def login_form_submission(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        username = request.POST.get("username")
        password = request.POST.get('password')
        user=auth.authenticate(username=username,password=password)

        if user is not None:
            auth.login(request,user)
            return render(request, 'video_conferencing/dashboard.html', {})