from django.urls import path

from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('', views.index),
    path('post/write', views.write, name='write'), 
    path('post/your-drafts', views.drafts, name='drafts'),
    path('post/your-posts', views.posts, name='posts'),

    path('<str:post_code>', views.commContent, name='content'),
    path('<str:post_code>/mastercases', views.commMastercases, name='mastercases'),
    path('<str:post_code>/counters', views.commCounters, name='counters'),
    path('<str:post_code>/dogs', views.commDogs, name='dogs'),

    path('robots.txt/', TemplateView.as_view(template_name="bots/robots.txt", content_type='text/plain'))
]