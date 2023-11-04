import json
import datetime
import re

from django.contrib.auth import get_user_model

from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from django.shortcuts import redirect

from channels.generic.websocket import AsyncWebsocketConsumer

User = get_user_model()

class HomeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.post_group_name = 'main'

        # Join post group
        await self.channel_layer.group_add(
            self.post_group_name, self.channel_name
        )

        await self.accept()
    

    async def disconnect(self, close_code):
        # Leave post group
        await self.channel_layer.group_discard(
            self.post_group_name, self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        user = self.scope["user"]

        text_data_json = json.loads(text_data)

        if 'ping' in text_data_json.keys():

            if text_data_json['ping'] == 'performance':
                await self.send(text_data=json.dumps({
                    'pong' : 'performance',
                }))

    async def update_post(self, event):
        post_code = event["post_code"]
        last_message_content = event["last_message_content"]

        await self.send(text_data=json.dumps({
            "post_code" : post_code,
            "last_message_content" : last_message_content,
        }))

    async def someone_typing(self, event):
        post_code = event["post_code"]

        await self.send(text_data=json.dumps({
            "data_point" : "someone_typing",
            "post_code" : post_code,
        }))

