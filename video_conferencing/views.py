from django.shortcuts import render
from .models import *

# Create your views here.

def home_page(request,room_id,user_name):
    return render(request, 'video_conferencing/home.html',{'room_id':room_id,'user_name':user_name})
