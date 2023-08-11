from django.urls import path 

from . import views

urlpatterns = [
    path('ws/<str:post_code>/chat', views.chat, name='chat')
]