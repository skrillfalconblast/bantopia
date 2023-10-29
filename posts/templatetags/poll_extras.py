from django import template
from django.contrib.auth import get_user_model

from django.utils.html import escape, escapejs

import re

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