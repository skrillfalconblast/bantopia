from django import template
from django.contrib.auth import get_user_model

from django.utils.html import escape
from django.utils import timezone

import re
import math

from datetime import datetime

User = get_user_model()

register = template.Library()

@register.filter
def truncate(value, end):
    words = value.split()
    if len(words) >= end:
        keep = words[0:end]
        keep[end-1] = keep[end-1]+"..."
    elif len(words) > 0:
        end = len(words)
        keep = words[0:end]
        keep[end-1] = keep[end-1]+"..."
    else:
        keep = words
    return " ".join(keep)

register.filter("truncate", truncate)

@register.filter
def truncatesmart(value, limit=80):
    """
    Truncates a string after a given number of chars keeping whole words.

    Usage:
        {{ string|truncatesmart }}
        {{ string|truncatesmart:50 }}
    """

    try:
        limit = int(limit)
    # invalid literal for int()
    except ValueError:
        # Fail silently.
        return value

    # Return the string itself if length is smaller or equal to the limit
    if len(value) <= limit:
        return value

    # Cut the string
    value = value[:limit]

    # Break into words and remove the last
    words = value.split(' ')[:-1]

    # Join the words and return
    return ' '.join(words) + '...'

@register.filter
def stripcommas(value):
    return re.sub(',', '', value)

@register.filter(name='times') 
def times(number):
    return range(number)

@register.filter
def replace_mentions(message):

    message_text = escape(message.message_content)

    if '@' in message_text:

        mentions = message.message_mentions.all()

        mentionArray = []

        mentionTuples = re.findall("(^|[^@\w])@(\w{1,20})", message_text)

        for mentionTuple in mentionTuples:
            mentionArray.append(mentionTuple[1])

        for mentioned_name in set(mentionArray):

            try:
                user = [mention for mention in list(mentions) if mention.display_name == mentioned_name]
            except:
                user = None

            if user:
                message_text = message_text.replace(f"@{mentioned_name}", f'<span class="color-{user[0].color}">@{mentioned_name}</span>')
            else:
                message_text = message_text.replace(f"@{mentioned_name}", f'<span class="color-OR">@{mentioned_name}</span>')

    return message_text

@register.filter
def convert_to_datetime(value):
    return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f%z')


@register.filter
def briefLongAgo(value):
    now = timezone.now()
    
    diff = now - value

    if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
        seconds = diff.seconds
        
        if seconds == 1:
            return str(seconds) +  " secs ago"
        
        else:
            return str(seconds) + " secs ago"

        

    if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600:
        minutes= math.floor(diff.seconds/60)

        if minutes == 1:
            return str(minutes) + " min ago"
        
        else:
            return str(minutes) + " mins ago"



    if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400:
        hours= math.floor(diff.seconds/3600)

        if hours == 1:
            return str(hours) + " r ago"

        else:
            return str(hours) + " hrs ago"

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
            return str(months) + " mnth ago"

        else:
            return "+1 mnths ago"


    if diff.days >= 365:
        years= math.floor(diff.days/365)

        if years == 1:
            return str(years) + " yr ago"

        else:
            return "+1 yrs ago"