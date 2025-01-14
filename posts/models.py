from django.db import models

from django.conf import settings

from django.template.defaultfilters import slugify

from django.urls import reverse

import time

# Create your models here.

class Post(models.Model):

    DECLARATION = "DE"
    THEORY = "TH"
    QUESTION = "QU"
    POST_TYPE_CHOICES = [
        (DECLARATION, "Declaration"),
        (THEORY, "Theory"),
        (QUESTION, "Question"),
    ]

    post_code = models.CharField(max_length=8)

    post_type = models.CharField(max_length=2, choices=POST_TYPE_CHOICES, default=DECLARATION) # This is names 'post_type' instead of simply 'type' because that conflicts with some python built-in variable name.
    post_title = models.CharField(max_length=255)
    post_desc = models.TextField()# Add max_length

    post_author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="post_author", on_delete=models.CASCADE)
    post_author_name = models.CharField(max_length=20)

    post_TPP = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="post_TPP", on_delete=models.SET_NULL, null=True, blank=True)
    post_PEN1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="post_PEN1", on_delete=models.SET_NULL, null=True, blank=True)

    post_datetime_created = models.DateTimeField(verbose_name='date and time created', auto_now_add=True)
    post_number_of_messages = models.IntegerField(default=0)
    post_timestamp_created = models.IntegerField() # Unix Timestamp for sorting calculations.

    post_number_of_yes_votes = models.IntegerField(default=0)
    post_number_of_no_votes = models.IntegerField(default=0)

    post_slug = models.SlugField(default='post', max_length=255)

    notified = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    def save(self, *args, **kwargs):
        self.post_timestamp_created = time.time()
        self.post_slug = slugify(self.post_title)
        super(Post, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('context', kwargs={'post_code': str(self.post_code), 'post_slug' : str(self.post_slug)})

class Tag(models.Model):
    tag_text = models.CharField(max_length=255)
    tag_post = models.ForeignKey('Post', on_delete=models.CASCADE)

class Vote(models.Model):
    vote_post = models.ForeignKey('Post', on_delete=models.CASCADE)
    vote_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    vote_type = models.BooleanField()

    vote_datetime = models.DateTimeField(verbose_name='date and time voted', auto_now=True)


# ----------------- Draft ---------------


class Draft(models.Model):

    DECLARATION = "DE"
    THEORY = "TH"
    QUESTION = "QU"
    DRAFT_TYPE_CHOICES = [
        (DECLARATION, "Declaration"),
        (THEORY, "Theory"),
        (QUESTION, "Question")
    ]

    draft_code = models.CharField(max_length=8)

    draft_type = models.CharField(max_length=2, choices=DRAFT_TYPE_CHOICES, default=DECLARATION)
    draft_title = models.CharField(max_length=100)
    draft_desc = models.TextField()# Add max_length

    draft_author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    draft_datetime_created = models.DateTimeField(verbose_name='date and time created', auto_now_add=True)

    draft_tags = models.CharField(max_length=200) # They are encoded in an alphanumeric string for ease of storage.

class Visit(models.Model):

    visit_post = models.ForeignKey('Post', on_delete=models.CASCADE)
    visit_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    visit_datetime = models.DateTimeField(auto_now_add=True)
    
class Splash(models.Model):
    splash_text = models.CharField()
    splash_datetime = models.DateTimeField(auto_now_add=True)