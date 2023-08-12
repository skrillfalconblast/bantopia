from django.shortcuts import render, redirect
from posts.models import Post, Vote
from .models import Message, Interaction

from django.contrib.auth import get_user_model

# Create your views here.

User = get_user_model()


def chat(request, post_code):

    if Post.objects.filter(post_code=post_code):

        user = request.user

        post = Post.objects.get(post_code=post_code)

        votes = {'y' : Vote.objects.filter(vote_post=post, vote_type=True).count(),
                 'n' : Vote.objects.filter(vote_post=post, vote_type=False).count()}

        messages = Message.objects.filter(message_post=post).select_related('message_author').order_by('-message_datetime_sent')[:50:-1]

        context = {'post' : post, 'messages' : messages, 'y' : votes["y"], 'n' : votes["n"]}

        if user.is_superuser:
            puppets = user.puppets.all()

            context['puppets'] = puppets

        return render(request, 'comms/chat.html', context)
    
    else:

        return redirect('/')