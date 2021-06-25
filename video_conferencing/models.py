from django.db import models
from django.contrib.auth.models import User



class Team(models.Model):
    team_id = models.AutoField(primary_key=True)
    team_name = models.CharField(max_length=200, null=False)
    data_formed = models.DateField(auto_now=True)

class User_Team(models.Model):
    user_name = models.CharField(User, max_length=200)
    team_id = models.IntegerField()
    is_admin=models.BooleanField(default=False)
