from django.urls import path

from django.views.generic import TemplateView

from . import views

urlpatterns = [
    # path('', views.index),
    # path('post/write', views.write, name='write'), 
    # path('post/your-drafts', views.drafts, name='drafts'),
    # path('post/your-posts', views.posts, name='posts'),

    # path('<str:post_code>/<str:post_slug>/', views.commContext, name='context'),
    # path('<str:post_code>/<str:post_slug>/mastercases', views.commMastercases, name='mastercases'),
    # path('<str:post_code>/<str:post_slug>/counters', views.commCounters, name='counters'),
    # path('<str:post_code>/<str:post_slug>/dogs', views.commDogs, name='dogs'),
    path('api/', views.PostAPI.as_view()),

    path('robots.txt/', TemplateView.as_view(template_name="bots/robots.txt", content_type='text/plain'))
]