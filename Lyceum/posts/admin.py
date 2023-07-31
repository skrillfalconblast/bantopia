from django.contrib import admin
from .models import Post, Tag, Vote, Draft, Visit


# Register your models here.

admin.site.register(Post)
admin.site.register(Tag)
admin.site.register(Vote)
admin.site.register(Draft)
admin.site.register(Visit)