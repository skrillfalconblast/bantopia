from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/(?P<post_code>\w+)/', consumers.ChatConsumer.as_asgi()),
]