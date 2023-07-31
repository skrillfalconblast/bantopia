from django.contrib import admin

from .models import Message, Interaction

# Register your models here.

admin.site.register(Message)
admin.site.register(Interaction)