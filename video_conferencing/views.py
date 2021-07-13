from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# check validity function returns true if the user is valid and is already part of the team


def checkValidity(user, team_id):
    if(User.objects.filter(username=user).exists()
       and User_Team.objects.filter(user_name=user, team_id=int(team_id)).exists() is not True):
        return True
    else:
        return False


# take the HTTP request as the input
# handles the login functionality
# redirects to the dashboard page on success


def login_page(request):
    if request.method != "POST":
        return render(request, 'video_conferencing/login.html', {})
    else:
        username = request.POST.get("username")
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)

        # checks for the user credentials
        if user is not None:
            auth.login(request, user)
            return redirect("/dashboard/0/")
        else:
            messages.info(request, "Invalid credentials")
            return redirect("/")


# handles the user sign-up functionality

def register_page(request):
    if request.method != "POST":
        return render(request, 'video_conferencing/register.html', {})
    else:
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get('email')
        password = request.POST.get('password')

        # checks for validity of the user information
        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            messages.info(request, "Username or email is already taken")
            return redirect("/register/")

        # saves it in the database
        user = User.objects.create_user(
            username=username, password=password, email=email, last_name=last_name, first_name=first_name)
        user.save()

        user = auth.authenticate(username=username, password=password)

        auth.login(request, user)
        return redirect("/dashboard/0/")

# @login_required, a decorator to make sure the requested page is only accessed by authenticated user
# this function is responsible for rendering the dashboard page for the user


@login_required
def dashboard_page(request, team_id):
    username = request.user.username
    user = User.objects.get(username=username)
    user_teams = User_Team.objects.filter(user_name=username)
    name = None
    if(team_id != '0'):
        team_members = User_Team.objects.filter(team_id=team_id)
    else:
        team_members = None

    # obtaining the team name
    if User_Team.objects.filter(
            user_name=user, team_id=int(team_id)).exists():
        team_name = User_Team.objects.filter(
            user_name=user, team_id=int(team_id))
        name = team_name[0].team_name

    # checking if the authenticated user is a member of the team or not
    if User_Team.objects.filter(
            user_name=user, team_id=int(team_id)).exists() or team_id == '0':
        return render(request, 'video_conferencing/dashboard.html', {"users": user, "user_teams": user_teams, "team_id": team_id, "name": name, "team_members": team_members})
    else:
        messages.info(
            request, "You are not permitted to access the group that you aren't part of")
        return redirect("/dashboard/0/")


# function to handle the group formation request
@login_required
def team_form_page(request):
    if request.method != "POST":
        return render(request, 'video_conferencing/team_register.html', {})
    else:
        team_name = request.POST.get("team_name")
        user_member = request.POST.get("user_member")

        # function to check the validity of the member user added by the admin
        # returns true if the member user is invalid or is same as the authenticated user
        if User.objects.filter(username=user_member).exists() is not True or user_member == request.user.username:
            messages.info(request, "Member user is invalid")
            return redirect("/team_form/")

        # saving it in the database
        team = Team()
        team.save()
        team_id = team.team_id
        user_team1 = User_Team(user_name=request.user.username,
                               team_id=team_id, team_name=team_name, is_admin=True)
        user_team1.save()
        user_team2 = User_Team(user_name=user_member,
                               team_id=team_id, team_name=team_name, is_admin=False)
        user_team2.save()
        link = "/dashboard/"+str(team_id) + '/'
        return redirect(link)

# function to add members to the pre-existing group

@login_required
def add_members_page(request, team_id):
    if request.method != "POST":
        return render(request, 'video_conferencing/add_members.html', {'team_id': team_id})
    else:
        user = request.user.username
        team_name = User_Team.objects.filter(
            user_name=user, team_id=int(team_id))
        name = team_name[0].team_name

        user1 = request.POST.get('user1')
        user2 = request.POST.get('user2')
        user3 = request.POST.get('user3')
        user4 = request.POST.get('user4')

        # check validity function returns true if the user is valid and is already part of the team
        if checkValidity(user1, team_id):
            user_team1 = User_Team(
                user_name=user1, team_id=int(team_id), team_name=name, is_admin=False)
        else:
            messages.info(request, "Invalid member entry")
            link = "/add_members/"+str(team_id) + '/'
            return redirect(link)

        if(user2 != ''):
            if checkValidity(user2, team_id):
                user_team2 = User_Team(
                    user_name=user2, team_id=int(team_id), team_name=name, is_admin=False)
            else:
                messages.info(request, "Invalid member entry")
                link = "/add_members/"+str(team_id) + '/'
                return redirect(link)

        if(user3 != ''):
            if checkValidity(user3, team_id):
                user_team3 = User_Team(
                    user_name=user3, team_id=int(team_id), team_name=name, is_admin=False)
            else:
                messages.info(request, "Invalid member entry")
                link = "/add_members/"+str(team_id) + '/'
                return redirect(link)

        if(user4 != ''):
            if checkValidity(user4, team_id):
                user_team4 = User_Team(
                    user_name=user4, team_id=int(team_id), team_name=name, is_admin=False)
            else:
                messages.info(request, "Invalid member entry")
                link = "/add_members/"+str(team_id) + '/'
                return redirect(link)

        # it is then finally inserted into the database if every user is validated
        user_team1.save()
        if(user2 != ''):
            user_team2.save()
        if(user3 != ''):
            user_team3.save()
        if(user4 != ''):
            user_team4.save()

        link = "/dashboard/"+str(team_id) + '/'
        return redirect(link)

# function to return video conferencing page

@login_required
def video_page(request, team_id):
    user_name = request.user.username
    # check if the user is part of the group
    if User_Team.objects.filter(
            user_name=user_name, team_id=int(team_id)).exists():
        return render(request, 'video_conferencing/videoPage.html', {'team_id': team_id, 'user_name': user_name})
    else:
        messages.info(
            request, "You are not permitted to access the call of the group that you aren't part of")
        return redirect("/dashboard/0/demo/")

# function to log the user out of the app

@login_required
def logout_page(request):
    auth.logout(request)
    return redirect("/")
