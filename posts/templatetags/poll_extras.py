from django import template
from re import sub

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
    return sub(',', '', value)

@register.filter(name='times') 
def times(number):
    return range(number)