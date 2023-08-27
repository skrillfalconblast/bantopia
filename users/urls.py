from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('create-profile/', views.createProfile, name='create_profile'),
    path('<str:display_name>/dashboard/', views.dashboard, name='dashboard'),
    path('<str:display_name>/edit-profile', views.edit_profile, name='edit_profile'),
    path('logout/', views.logout, name='logout')
]