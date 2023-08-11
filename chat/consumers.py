import json
import datetime

from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model

from channels.db import database_sync_to_async

from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Message, Interaction
from posts.models import Post, Vote
from users.models import WatchlistActivity, Report

from django.utils import timezone
from django.db.models import Sum

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    # Function to used to fetch user asynchronously
    @database_sync_to_async
    def get_post(self):
        try:
            post = Post.objects.get(post_code=self.post_code)
            return post
        except Post.DoesNotExist:
            return None
        


# --------------------------- Watchlist Activity Handlers --------------------------------


    @database_sync_to_async
    def find_message(self, **kwargs):
        try:
            message = Message.objects.get(**kwargs)
            return message
        except Message.DoesNotExist:
            return None
        
    @database_sync_to_async
    def handle_engage(self, user): # Can't plug in normal async functions because they reutrn co-routinie objectcs.
        try:
            try:
                post = Post.objects.get(post_code=self.post_code)
            except Post.DoesNotExist:
                post = None

            try:
                message = Message.objects.get(message_post=post, message_author=user)
            except Message.DoesNotExist:
                message =  None

            if not message: # We pass in user as an parameter because it would be a needless hasstle to pass kwargs instead (change if needed).
                WatchlistActivity.objects.create(watchlist_activity_user=user, watchlist_activity_post=post, watchlist_activity_type=WatchlistActivity.ENGAGE)
        except:
            pass

    @database_sync_to_async
    def handle_active(self, user): # Can't plug in normal async functions because they reutrn co-routinie objectcs.
        try:
            try:
                post = Post.objects.get(post_code=self.post_code)
            except Post.DoesNotExist:
                post = None

            try:
                last_timeperiod = timezone.now() - datetime.timedelta(minutes=7)
                messages = Message.objects.filter(message_post=post, message_author=user, message_datetime_sent__gt=last_timeperiod)
            except Message.DoesNotExist:
                messages =  None

            if messages.count() == 15: # We pass in user as an parameter because it would be a needless hasstle to pass kwargs instead (change if needed).
                WatchlistActivity.objects.create(watchlist_activity_user=user, watchlist_activity_post=post, watchlist_activity_type=WatchlistActivity.ACTIVE)

        except:
            pass

# --------------------------------- FOR CHAT -----------------------------

    @database_sync_to_async
    def find_interaction(self, message, user, **kwargs):
        try:
            interaction = Interaction.objects.get(interaction_message=message, interaction_user=user, **kwargs)
            return interaction
        except Interaction.DoesNotExist:
            return None

    # I use this to log the message in the DB
    @database_sync_to_async
    def log_message(self, message_content, user):

        message_code = get_random_string(length=12)
        post = Post.objects.get(post_code=self.post_code)

        message = Message.objects.create(message_code=message_code, message_post=post, message_content=message_content, 
                               message_author=user, message_author_name=user.display_name)
        
        post.post_number_of_messages += 1
        post.save()

        return message
    
    @database_sync_to_async
    def handle_interaction(self, message, user, option):
        
        if option == 'LIKE':
            try:
                interaction = Interaction.objects.create(interaction_message=message, interaction_user=user, interaction_type='L')
                message.message_score += 1
                message.save()
                return interaction
            except:
                return None
        
        elif option == 'DISLIKE':

            try:
                interaction = Interaction.objects.create(interaction_message=message, interaction_user=user, interaction_type='D')
                message.message_score -= 1
                message.save()
                return interaction
            except:
                return None
        

        elif option == 'UNLIKE':
            try:
                interaction = Interaction.objects.get(interaction_message=message, interaction_user=user, interaction_type=Interaction.LIKE)

                message.message_score -= 1
                message.save()

                interaction = Interaction.objects.get(interaction_message=message, interaction_user=user)
                interaction.delete()
            except Interaction.DoesNotExist:
                pass

        elif option == 'UNDISLIKE':
            try: 
                interaction = Interaction.objects.get(interaction_message=message, interaction_user=user, interaction_type=Interaction.DISLIKE)
                message.message_score += 1 
                message.save()
            
                interaction = Interaction.objects.get(interaction_message=message, interaction_user=user)
                interaction.delete()
            except Interaction.DoesNotExist:
                pass

    @database_sync_to_async
    def dog_check(self, message):
        post = Post.objects.get(post_code=self.post_code)
        author = message.message_author
        
        score = Message.objects.filter(message_post=post, message_author=author).aggregate(Sum('message_score'))
        if score['message_score__sum'] > 2:
            TPP_score = Message.objects.filter(message_post=post, message_author=post.post_TPP).aggregate(Sum('message_score'))
            if TPP_score['message_score__sum']:
                if score['message_score__sum'] > TPP_score['message_score__sum']:
                    post.post_TPP = author
                    post.save()
                    WatchlistActivity.objects.create(watchlist_activity_user=author, watchlist_activity_post=post, watchlist_activity_type=WatchlistActivity.POPULAR)
            else:
                post.post_TPP = author
                post.save()
                WatchlistActivity.objects.create(watchlist_activity_user=author, watchlist_activity_post=post, watchlist_activity_type=WatchlistActivity.POPULAR)

        if score['message_score__sum'] < -2:
            PEN1_score = Message.objects.filter(message_post=post, message_author=post.post_PEN1).aggregate(Sum('message_score'))
            if PEN1_score['message_score__sum']:
                if score['message_score__sum'] < PEN1_score['message_score__sum']:
                    post.post_PEN1 = author
                    post.save()
                    WatchlistActivity.objects.create(watchlist_activity_user=author, watchlist_activity_post=post, watchlist_activity_type=WatchlistActivity.INFAMOUS)
            else:
                post.post_PEN1 = author
                post.save()
                WatchlistActivity.objects.create(watchlist_activity_user=author, watchlist_activity_post=post, watchlist_activity_type=WatchlistActivity.INFAMOUS)

        number_of_likes = Interaction.objects.filter(interaction_message=message, interaction_type=Interaction.LIKE).count()
        number_of_dislikes = Interaction.objects.filter(interaction_message=message, interaction_type=Interaction.DISLIKE).count()

        if number_of_likes >= 2 and number_of_dislikes >= 2:
            interaction_ratio = number_of_dislikes/number_of_likes
            if interaction_ratio < 1.20 and interaction_ratio > 0.80: # 20% either way
                WatchlistActivity.objects.create(watchlist_activity_user=author, watchlist_activity_post=post, watchlist_activity_type=WatchlistActivity.CONTROVERSIAL)
            
    @database_sync_to_async
    def handle_command(self, message, user):
        try:
            command = message.split(' ')
            command_type = command[0]

            command_type_list = ['/watch', '/unwatch', '/report']

            if command_type in command_type_list:

                    name = command[1]

                    try:
                        user_referenced = User.objects.get(display_name=name)
                    except:
                        user_referenced = None

                    if user_referenced:
                    
                        if command_type == '/watch':

                            user.watching.add(user_referenced)
                            return f"You successfully started watching {name}! I wonder why?"

                        elif command_type == '/unwatch':

                            user.watching.remove(user_referenced)
                            return f"You successfully unwatched {name}, have fun not watching them!"
                        
                        elif command_type == '/report':

                            name = command[1]
                            text = message.split('"')[1::2][0]

                            Report.objects.create(report_reporter=user, report_reporter_name=user.display_name, report_reported=user_referenced, report_reported_name=name, report_reason=text)
                            return f"You successfully reported {name}, hopefully it was for a good reason."

                        else:
                            return f"Tut, Tut. That command isn't real. Have no fear, more will be revealed soon."
                    else:
                        return f"How peculiar, {name} doesn't seem to exist...\ Stalking phantoms, are we?"
            else:
                return f"Tut, Tut. That command isn't real. Have no fear, more will be revealed soon."
        except:
            return f"An error occured. Remember: a samurai doesn't slash wildly, he strikes incisivly."
                

    @database_sync_to_async
    def handle_vote(self, vote_type, user):
        post = Post.objects.get(post_code=self.post_code)

        if vote_type == 'Y':

            if Vote.objects.filter(vote_post=post, vote_type=False, vote_user=user):
            
                vote = Vote.objects.get(vote_post=post, vote_user=user)
                vote.vote_type = True
                vote.save()

                post.post_number_of_no_votes -= 1
                post.post_number_of_yes_votes += 1
                post.save()

                return vote
            
            elif Vote.objects.filter(vote_post=post, vote_type=True, vote_user=user):
            
                vote = Vote.objects.get(vote_post=post, vote_user=user)
                vote.delete()

                post.post_number_of_yes_votes -= 1
                post.save()

            else:

                vote = Vote.objects.create(vote_post=post, vote_type=True, vote_user=user)

                post.post_number_of_yes_votes += 1
                post.save()

                return vote

        elif vote_type == 'N':
            if Vote.objects.filter(vote_post=post, vote_type=True, vote_user=user):

                vote = Vote.objects.get(vote_post=post, vote_user=user)
                vote.vote_type = False
                vote.save()

                post.post_number_of_yes_votes -= 1
                post.post_number_of_no_votes += 1
                post.save()

                return vote
            
            elif Vote.objects.filter(vote_post=post, vote_type=False, vote_user=user):

                vote = Vote.objects.get(vote_post=post, vote_user=user)
                vote.delete()

                post.post_number_of_no_votes -= 1
                post.save()

            else:
                vote = Vote.objects.create(vote_post=post, vote_type=False, vote_user=user)

                post.post_number_of_no_votes += 1
                post.save()

                return vote

    @database_sync_to_async
    def find_vote(self, user):
        try:
            post = Post.objects.get(post_code=self.post_code)
            vote = Vote.objects.get(vote_post=post, vote_user=user)

            if vote:
                return vote
        except Vote.DoesNotExist:
            return None
        
    @database_sync_to_async
    def tally_votes(self):

        post = Post.objects.get(post_code=self.post_code)

        y_votes = Vote.objects.filter(vote_post=post, vote_type=True).count()
        n_votes = Vote.objects.filter(vote_post=post, vote_type=False).count()

        tally = {
            'y' : y_votes,
            'n' : n_votes
        }

        return tally


    async def connect(self):
        self.post_code = self.scope["url_route"]["kwargs"]["post_code"]
        self.post_group_name = 'chat_%s' % self.post_code

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

        if 'message_id' in text_data_json.keys() and text_data_json['trigger'] == 'hover':

            if user.is_authenticated:

                message_id = text_data_json['message_id']
                message_code = message_id[4:] # Get the message code without the 'msg_' part

                message = await self.find_message(message_code=message_code)

                if await self.find_interaction(message, user):
                    interaction = await self.find_interaction(message, user)
                    if interaction.interaction_type == Interaction.LIKE:
                        await self.send(text_data=json.dumps({
                            'message_id' : message_id,
                            'state' : 'liked'
                        }))
                    elif interaction.interaction_type == interaction.DISLIKE:
                        await self.send(text_data=json.dumps({
                            'message_id' : message_id,
                            'state' : 'disliked'
                        }))

                else:
                    await self.send(text_data=json.dumps({
                        'message_id' : message_id,
                        'state' : 'neutral'
                    }))
            else:
                pass

        elif 'message_id' in text_data_json.keys() and text_data_json['trigger'] == 'click':
            message_id = text_data_json['message_id']
            message_code = message_id[4:]

            user = self.scope["user"]

            if text_data_json['attempt'] == 'like':
                if user.is_authenticated:

                    message = await self.find_message(message_code=message_code)

                    if await self.find_interaction(message, user):
                        if (await self.find_interaction(message, user, interaction_type=Interaction.LIKE)):
                            await self.send(text_data=json.dumps({
                                'message_id' : message_id,
                                'action' : 'unlike'
                            }))

                            await self.handle_interaction(message, user, 'UNLIKE')
                            await self.channel_layer.group_send(
                                self.post_group_name, {"type" : "message_interaction", "message_id" :  message_id, "interaction" : "unlike", "interacting_channel" : self.channel_name}
                            )

                            await self.dog_check(message)
                    else:
                        await self.send(text_data=json.dumps({
                            'message_id' : message_id,
                            'action' : 'like'
                        }))

                        await self.handle_interaction(message, user, 'LIKE')
                        await self.channel_layer.group_send(
                            self.post_group_name, {"type" : "message_interaction", "message_id" :  message_id, "interaction" : "like", "interacting_channel" : self.channel_name}
                        )

                        await self.dog_check(message)

            elif text_data_json['attempt'] == 'dislike':
                if user.is_authenticated:

                    message = await self.find_message(message_code=message_code)

                    if await self.find_interaction(message, user):
                        if await self.find_interaction(message, user, interaction_type=Interaction.DISLIKE):
                            await self.find_interaction(message, user, interaction_type=Interaction.DISLIKE)
                            await self.send(text_data=json.dumps({
                                'message_id' : message_id,
                                'action' : 'undislike'
                            }))
                            await self.handle_interaction(message, user, 'UNDISLIKE')
                            await self.channel_layer.group_send(
                                self.post_group_name, {"type" : "message_interaction", "message_id" :  message_id, "interaction" : "undislike", "interacting_channel" : self.channel_name}
                            )

                            await self.dog_check(message)
                    else:
                        await self.send(text_data=json.dumps({
                            'message_id' : message_id,
                            'action' : 'dislike'
                        }))
                        await self.handle_interaction(message, user, 'DISLIKE')
                        await self.channel_layer.group_send(
                            self.post_group_name, {"type" : "message_interaction", "message_id" :  message_id, "interaction" : "dislike", "interacting_channel" : self.channel_name}
                        )

                        await self.dog_check(message)

        elif 'message' in text_data_json.keys():
            user = self.scope["user"]

            if user.is_authenticated:

                message = text_data_json["message"]

                if not message.startswith('/'):

                    await self.handle_engage(user)
                    await self.handle_active(user)

                    new_message = await self.log_message(message, user)

                    # Send message to post group
                    await self.channel_layer.group_send(
                        self.post_group_name, {"type" : "chat_message", "message_code" :  new_message.message_code, "message" : new_message.message_content, "author_name" : new_message.message_author_name, "author_color" : new_message.message_author.color}
                    )
                else:

                    result = await self.handle_command(message, user)

                    await self.send(text_data=json.dumps({
                        "alert" : "command_success",
                        "message" : result,
                    }))



        elif 'voting' in text_data_json.keys():
            user = self.scope["user"]

            if user.is_authenticated:

                vote = text_data_json["voting"]

                if vote == 'N':

                    await self.handle_vote('N', self.scope["user"])

                    tally = await self.tally_votes()

                    await self.send(text_data=json.dumps({
                        'y' : tally['y'],
                        'n' : tally['n'],
                    }))

                elif vote == 'Y':

                    await self.handle_vote('Y', self.scope["user"])

                    tally = await self.tally_votes()

                    await self.send(text_data=json.dumps({
                        'y' : tally['y'],
                        'n' : tally['n'],
                    }))

    # Receive message from post group
    async def chat_message(self, event):
        message_code = event["message_code"]
        message = event["message"]
        author_name = event["author_name"]
        color = event["author_color"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "message_code" : message_code,
            "message" : message,
            "author" : author_name,
            "author_color" : color,
            }))
        
    async def message_interaction(self, event):
        message_id = event["message_id"]
        interaction = event["interaction"]
        interacting_channel = event["interacting_channel"]

        if self.channel_name != interacting_channel:
            await self.send(text_data=json.dumps({
                "message_id" : message_id,
                "interaction" : interaction,
            }))