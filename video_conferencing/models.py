from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import AutoField

# Table for the Team/Group, where team id is the primary key


class Team(models.Model):
    team_id = models.AutoField(primary_key=True)
    date_formed = models.DateField(auto_now=True)

# Table to store information about the users association with the teams


class User_Team(models.Model):
    user_name = models.CharField(User, max_length=200)
    team_id = models.IntegerField()
    team_name = models.CharField(max_length=200, default="demo")
    is_admin = models.BooleanField(default=False)

# Table to store the chats of the respective teams


class Chat(models.Model):
    team_id = models.IntegerField()
    message = models.CharField(max_length=1000)
