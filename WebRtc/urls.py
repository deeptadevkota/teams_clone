""" URL Configuration

The `urlpatterns` list routes URLs to views. For more information :
    https://docs.djangoproject.com/en/2.0/topics/http/urls/

"""
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('video_conferencing.urls')),
]
