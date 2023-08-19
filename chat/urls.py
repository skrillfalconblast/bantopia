from django.urls import path 

from . import views

urlpatterns = [
    path('ws/<str:post_code>/<str:post_slug>/chat', views.chat, name='chat')
]