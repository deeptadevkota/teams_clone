from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def login_page(request):
    if request.method != "POST":
        return render(request, 'video_conferencing/login.html', {})
    else:
        username = request.POST.get("username")
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect("/dashboard/0/demo/")
        else:
            messages.info(request, "Invalid credentials")
            return redirect("/login/")


def register_page(request):
    if request.method != "POST":
        return render(request, 'video_conferencing/register.html', {})
    else:
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            messages.info(request, "Username or email is already taken")
            return redirect("/register/")

        user = User.objects.create_user(
            username=username, password=password, email=email, last_name=last_name, first_name=first_name)
        user.save()

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect("/dashboard/0/demo/")


@login_required
def dashboard_page(request, team_id, name):
    username = request.user.username
    user = User.objects.get(username=username)
    user_teams = User_Team.objects.filter(user_name=username)
    if(team_id != '0'):
        team_members = User_Team.objects.filter(team_id=team_id)
    else:
        team_members = None
    return render(request, 'video_conferencing/dashboard.html', {"users": user, "user_teams": user_teams, "team_id": team_id, "name": name, "team_members": team_members})


@login_required
def team_form_page(request):
    if request.method != "POST":
        return render(request, 'video_conferencing/team_register.html', {})
    else:
        team_name = request.POST.get("team_name")
        user_member = request.POST.get("user_member")
        if User.objects.filter(username=user_member).exists() is not True or user_member == request.user.username:
            messages.info(request, "Member user is invalid")
            return redirect("/team_form/")

        team = Team()
        team.save()
        team_id = team.team_id
        user_team1 = User_Team(user_name=request.user.username,
                               team_id=team_id, team_name=team_name, is_admin=True)
        user_team1.save()
        user_team2 = User_Team(user_name=user_member,
                               team_id=team_id, team_name=team_name, is_admin=False)
        user_team2.save()
        link = "/dashboard/"+str(team_id) + '/' + team_name + '/'
        return redirect(link)


@login_required
def add_members_page(request, team_id, name):
    if request.method != "POST":
        return render(request, 'video_conferencing/add_members.html', {'team_id': team_id, "name": name})
    else:
        user1 = request.POST.get('user1')
        user2 = request.POST.get('user2')
        user3 = request.POST.get('user3')
        user4 = request.POST.get('user4')

        if(User.objects.filter(username=user1).exists()
           and User_Team.objects.filter(user_name=user1, team_id=int(team_id)).exists() is not True):
            user_team1 = User_Team(
                user_name=user1, team_id=int(team_id), team_name=name, is_admin=False)
        else:
            messages.info(request, "Invalid member entry")
            link = "/add_members/"+str(team_id) + '/' + str(name) + '/'
            return redirect(link)

        if(user2 != ''):
            if(User.objects.filter(username=user2).exists()
               and User_Team.objects.filter(user_name=user2, team_id=int(team_id)).exists() is not True):
                user_team2 = User_Team(
                    user_name=user2, team_id=int(team_id), team_name=name, is_admin=False)
            else:
                messages.info(request, "Invalid member entry")
                link = "/add_members/"+str(team_id) + '/' + str(name) + '/'
                return redirect(link)

        if(user3 != ''):
            if(User.objects.filter(username=user3).exists() and
               User_Team.objects.filter(user_name=user3, team_id=int(team_id)).exists() is not True):
                user_team3 = User_Team(
                    user_name=user3, team_id=int(team_id), team_name=name, is_admin=False)
            else:
                messages.info(request, "Invalid member entry")
                link = "/add_members/"+str(team_id) + '/' + str(name) + '/'
                return redirect(link)

        if(user4 != ''):
            if(User.objects.filter(username=user4).exists() and
               User_Team.objects.filter(user_name=user4, team_id=int(team_id)).exists() is not True):
                user_team4 = User_Team(
                    user_name=user4, team_id=int(team_id), team_name=name, is_admin=False)
            else:
                messages.info(request, "Invalid member entry")
                link = "/add_members/"+str(team_id) + '/' + str(name) + '/'
                return redirect(link)

        user_team1.save()
        if(user2 != ''):
            user_team2.save()
        if(user3 != ''):
            user_team3.save()
        if(user4 != ''):
            user_team4.save()

        link = "/dashboard/"+str(team_id) + '/' + str(name) + '/'
        return redirect(link)


@login_required
def home_page(request, room_id, user_name):
    return render(request, 'video_conferencing/home.html', {'room_id': room_id, 'user_name': user_name})


@login_required
def logout_page(request):
    auth.logout(request)
    return redirect("/login/")
