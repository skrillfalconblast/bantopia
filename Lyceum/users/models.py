from django.db import models
from django.conf import settings
from django.utils import timezone

from django.contrib.auth.models import AbstractBaseUser
from .managers import UserManager
from django.contrib.auth.models import PermissionsMixin

from posts.models import Post

import math

# Create your models here.

class User(AbstractBaseUser, PermissionsMixin):
    ORANGE = "OR"
    BLUE = "BL"
    GREEN = "GR"
    RED = "RE"
    PURPLE = "PU"
    PINK = "PI"
    MAROON = "MA"
    AQUA = "AQ"
    
    COLOR_CHOICES = [
        (ORANGE, "Orange"),
        (BLUE, "Blue"),
        (GREEN, "Green"),
        (RED, "Red"),
        (PURPLE, "Purple"),
        (PINK, "Pink"),
        (MAROON, "Maroon"),
        (AQUA, "Aqua")
    ]

    display_name = models.CharField(max_length=20, unique=True) 
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=128)

    color = models.CharField(max_length=2, choices=COLOR_CHOICES, default=ORANGE)

    date_joined = models.DateField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    watching = models.ManyToManyField('self', symmetrical=False, blank=True)
    history = models.ManyToManyField(Post, through='posts.Visit')

    USERNAME_FIELD = 'display_name'

    REQUIRED_FIELDS = ['email', 'password']

    objects = UserManager()

    def has_perm(self, perm, obj=None):
        return self.is_superuser
    
    def has_module_perms(self, app_label):
        return self.is_superuser
    
    def __str__(self):
        return self.display_name
    
    ordering = ('display_name',)


class WatchlistActivity(models.Model):
    ACTIVE = "ACTIVE"
    DECLARE = "DECLARE"
    THEORISE = "THEORISE"
    ENGAGE = "ENGAGE"
    POPULAR = "POPULAR"
    INFAMOUS = "INFAMOUS"
    CONTROVERSIAL = "CONTROVERSIAL"
    PEN1 = "PEN1"
    TPP = "TPP"

    WATCHLIST_ACTIVITY_TYPE_CHOICES = [
        (ACTIVE, 'Active'),
        (DECLARE, 'Declare'),
        (THEORISE, 'Theorise'),
        (ENGAGE, 'Engage'),
        (POPULAR, 'Popular'),
        (INFAMOUS, 'Infamous'),
        (CONTROVERSIAL, 'Controversial'),
    ]

    watchlist_activity_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    watchlist_activity_post = models.ForeignKey('posts.post', on_delete=models.CASCADE)
    watchlist_activity_type = models.CharField(max_length=255, choices=WATCHLIST_ACTIVITY_TYPE_CHOICES)

    watchlist_activity_datetime = models.DateTimeField(auto_now_add=True)

    def longAgo(self):
        now = timezone.now()
        
        diff = now - self.watchlist_activity_datetime

        if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
            seconds = diff.seconds
            
            if seconds == 1:
                return str(seconds) +  "second ago"
            
            else:
                return str(seconds) + " seconds ago"

            

        if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600:
            minutes= math.floor(diff.seconds/60)

            if minutes == 1:
                return str(minutes) + " minute ago"
            
            else:
                return str(minutes) + " minutes ago"



        if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400:
            hours= math.floor(diff.seconds/3600)

            if hours == 1:
                return str(hours) + " hour ago"

            else:
                return str(hours) + " hours ago"

        # 1 day to 30 days
        if diff.days >= 1 and diff.days < 30:
            days= diff.days
        
            if days == 1:
                return str(days) + " day ago"

            else:
                return str(days) + " days ago"

        if diff.days >= 30 and diff.days < 365:
            months= math.floor(diff.days/30)
            

            if months == 1:
                return str(months) + " month ago"

            else:
                return str(months) + " months ago"


        if diff.days >= 365:
            years= math.floor(diff.days/365)

            if years == 1:
                return str(years) + " year ago"

            else:
                return str(years) + " years ago"


class Report(models.Model):

    report_reporter = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="report_reporter", on_delete=models.SET_NULL, null=True)
    report_reporter_name = models.CharField(max_length=20)

    report_reported = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="report_reported", on_delete=models.SET_NULL, null=True)
    report_reported_name = models.CharField(max_length=20)

    report_reason = models.TextField()

    report_datetime = models.DateTimeField(auto_now_add=True)