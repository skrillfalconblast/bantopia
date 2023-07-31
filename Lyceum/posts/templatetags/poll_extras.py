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
def stripcommas(value):
    return sub(',', '', value)