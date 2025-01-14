"""Lyceum URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
# from .sitemaps import PostSitemap

sitemaps = {
    # "posts": PostSitemap,
}

urlpatterns = [
    path("__debug__/", include("debug_toolbar.urls")),
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    path('admins_den/', admin.site.urls),
    path('', include('users.urls')),
    path('', include('posts.urls')),
    path('', include('chat.urls')),

    path(
        "sitemap.xml/",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    )
]


