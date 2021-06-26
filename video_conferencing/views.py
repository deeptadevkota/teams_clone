from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.models import User, auth


def home_page(request, room_id, user_name):
    return render(request, 'video_conferencing/home.html', {'room_id': room_id, 'user_name': user_name})


def login_page(request):
    if request.method != "POST":
        return render(request, 'video_conferencing/login.html', {})
    else:
        username = request.POST.get("username")
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect("/dashboard/0")


def register_page(request):
    if request.method != "POST":
        return render(request, 'video_conferencing/register.html', {})
    else:
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = User.objects.create_user(
            username=username, password=password, email=email, last_name=last_name, first_name=first_name)
        user.save()

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect("/dashboard/0")


def dashboard_page(request,team_id):
    username = request.user.username
    user = User.objects.get(username=username)
    user_teams = User_Team.objects.filter(user_name=username)
    return render(request, 'video_conferencing/dashboard.html', {"users": user, "user_teams": user_teams, "team_id":team_id})


def team_form_page(request):
    if request.method != "POST":
        return render(request, 'video_conferencing/team_register.html', {})
    else:
        team_name = request.POST.get("team_name")
        user_member = request.POST.get("user_member")

def logout_page(request):
    auth.logout(request)
    return redirect("/login/")
