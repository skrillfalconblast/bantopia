from django.db import models
from django.conf import settings

# Create your models here.



class Message(models.Model):
    message_code = models.CharField(max_length=12, unique=True)

    message_post = models.ForeignKey('posts.Post', on_delete=models.CASCADE)
    message_content = models.TextField()
    message_score = models.IntegerField(default=0)

    message_datetime_sent = models.DateTimeField(verbose_name='date and time sent', auto_now_add=True)

    message_author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message_author_name = models.CharField(verbose_name='display name of author', max_length=20) # So if the author's account is deleted the name is still stored for display purposes

class Interaction(models.Model):
    LIKE = 'L'
    DISLIKE = 'D'
    INTERACTION_CHOICES = [
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
    ]

    interaction_message = models.ForeignKey('Message', on_delete=models.CASCADE)
    interaction_user = models.ForeignKey('users.User', on_delete=models.CASCADE)

    interaction_type = models.CharField(max_length=1, choices=INTERACTION_CHOICES, default=LIKE)

    interaction_datetime = models.DateTimeField(verbose_name='date and time of the like', auto_now=True)