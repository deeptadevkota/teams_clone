from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import AutoField


class Team:
    team_id = models.AutoField(primary_key=True)
    date_formed = models.DateField(auto_now=True)


class User_Team(models.Model):
    user_name = models.CharField(User, max_length=200)
    team_id = models.IntegerField()
    team_name = models.CharField(max_length=200, default="demo")
    is_admin = models.BooleanField(default=False)
