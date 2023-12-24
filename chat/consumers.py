import json
import datetime
import re

from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model

from channels.db import database_sync_to_async
from django.shortcuts import redirect

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Message, Interaction
from posts.models import Post, Vote
from users.models import WatchlistActivity, Report, Ban

from django.utils import timezone
from django.db.models import Sum

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    # Function to used to fetch post asynchronously
    @database_sync_to_async
    def get_post(self):
        try:
            post = Post.objects.get(post_code=self.post_code)
            return post
        except Post.DoesNotExist:
            return None
        
    # Function to used to fetch user asynchronously
    @database_sync_to_async
    def get_user(self, display_name):
        try:
            user = User.objects.get(display_name=display_name)
            return user
        except User.DoesNotExist:
            return None
        
    @database_sync_to_async
    def get_author(self, message):
        try:
            message_author = message.message_author
            return message_author
        except:
            return None
        
    @database_sync_to_async 
    def get_unloaded_messages(self, message_code): 
        post = Post.objects.get(post_code=self.post_code)
        
        last_message_datetime_sent = Message.objects.get(message_code=message_code, message_post=post).message_datetime_sent

        if last_message_datetime_sent:
            unloaded_messages = Message.objects.filter(message_post=post, message_datetime_sent__gt=last_message_datetime_sent)
            return unloaded_messages
        
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
    def handle_active(self, user): # Can't plug in normal async functions because they reutrn co-routinie objetcs.
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

# -------------------------------- For Notifications --------------------------------

    @database_sync_to_async
    def notify(self):

        # Gets the post (exactly the same logic as the get_post function)
        try:
            post = Post.objects.get(post_code=self.post_code)
        except Post.DoesNotExist:
            post = None
        
        users = User.objects.all()

        post.notified.set(users)

    @database_sync_to_async
    def denotify(self, user):
        try:
            post = Post.objects.get(post_code=self.post_code)
        except Post.DoesNotExist:
            post = None

        post.notified.remove(user)

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

        if user:

            message = Message.objects.create(message_code=message_code, message_post=post, message_content=message_content, 
                                message_author=user, message_author_name=user.display_name)
        else:
            message = Message.objects.create(message_code=message_code, message_post=post, message_content=message_content, 
                    message_author=user, message_author_name="Anon")
        
        if '@' in message_content:
        
            mentionTuples = re.findall("(^|[^@\w])@(\w{1,20})", message_content)

            mentionArray = []

            for mentionTuple in mentionTuples:

                mentioned_user_display_name = mentionTuple[1]

                mentionArray.append(mentioned_user_display_name)
            
            mentioned_users = User.objects.filter(display_name__in=mentionArray)

            if mentioned_users:
                message.message_mentions.add(*mentioned_users)

        post.post_number_of_messages += 1
        post.save()

        return message
    
    @database_sync_to_async
    def edit_message(self, message_code, edit_content, user):
        try:
            message = Message.objects.get(message_code=message_code)
            if message.message_author == user:
                message.message_content = edit_content
                message.save()
            else:
                message = None
        except Message.DoesNotExist:
            message = None
        
        return message
    
    @database_sync_to_async
    def handle_interaction(self, message, user, option):
        if option == 'LIKE':

            # Check if a dislike interaction for the same message exists.
            try:
                dislike_interaction = Interaction.objects.get(interaction_message=message, interaction_user=user, interaction_type=Interaction.DISLIKE)
            except Interaction.DoesNotExist:
                dislike_interaction = None

            if dislike_interaction:
                try:
                    interaction = Interaction.objects.get(interaction_message=message, interaction_user=user)
                    interaction.interaction_type = Interaction.LIKE
                    interaction.save()

                    message.message_score += 2
                    message.save()
                    return interaction
                except:
                    return None
            else:
                try:
                    interaction = Interaction.objects.create(interaction_message=message, interaction_user=user, interaction_type=Interaction.LIKE)
                    message.message_score += 1
                    message.save()
                    return interaction
                except:
                    return None
        
        elif option == 'DISLIKE':

            # Check if a like interaction for the same message exists.
            try:
                like_interaction = Interaction.objects.get(interaction_message=message, interaction_user=user, interaction_type=Interaction.LIKE)
            except Interaction.DoesNotExist:
                like_interaction = None

            if like_interaction:
                try:
                    interaction = Interaction.objects.get(interaction_message=message, interaction_user=user)
                    interaction.interaction_type = Interaction.DISLIKE
                    interaction.save()

                    message.message_score -= 2
                    message.save()
                    return interaction
                except:
                    return None
            else:
                try:
                    interaction = Interaction.objects.create(interaction_message=message, interaction_user=user, interaction_type=Interaction.DISLIKE)

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

    @database_sync_to_async
    def contrib_check(self, user):
        post = Post.objects.get(post_code=self.post_code)

        if user.pk in Message.objects.filter(message_post=post).select_related('message_author').distinct('message_author').values_list('message_author', flat='true'):
            return True
        else:
            return False
    
    @database_sync_to_async
    def ban_check(self, user):
        if Ban.objects.filter(banned_user=user):
            return True
        else:
            return False

    async def redirectTo(self, url):
        return redirect(url)

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
    async def receive(self, text_data=None, bytes_data=None):
        user = self.scope["user"]

        if text_data and not bytes_data:

            text_data_json = json.loads(text_data)

            if 'target' in text_data_json.keys() and 'message_id' in text_data_json.keys() and 'trigger' in text_data_json.keys():
                if text_data_json["trigger"] == 'hover':

                    if user.is_authenticated:

                        if text_data_json["target"] == 'message':

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

                            if 'puppet' in text_data_json.keys() and user.is_superuser:

                                puppet_name = text_data_json["puppet"]
                                puppet = await self.get_user(puppet_name)

                                if await self.get_author(message) == puppet:

                                    await self.send(text_data=json.dumps({
                                        'message_id' : message_id,
                                        'switch' : 'native'
                                    }))

                                else:
                                    await self.send(text_data=json.dumps({
                                        'message_id' : message_id,
                                        'switch' : 'foreign'
                                    }))

                        if text_data_json["target"] == "content":

                            if user.is_authenticated:

                                message_id = text_data_json['message_id']
                                message_code = message_id[4:] # Get the message code without the 'msg_' part

                                message = await self.find_message(message_code=message_code)



                elif text_data_json["trigger"] == "click":

                    if user.is_authenticated:

                        message_id = text_data_json['message_id']
                        message_code = message_id[4:]

                        if text_data_json["target"] == 'tag':

                            message = await self.find_message(message_code=message_code)
                            message_author = await self.get_author(message=message)

                            if 'puppet' in text_data_json.keys() and user.is_superuser:

                                puppet_name = text_data_json['puppet']

                                puppet = await self.get_user(puppet_name)

                                if message_author != puppet:

                                    puppet_name = text_data_json['puppet']

                                    puppet = await self.get_user(puppet_name)
                                    
                                    if text_data_json['attempt'] == 'like':

                                        if (await self.find_interaction(message, puppet, interaction_type=Interaction.LIKE)): # We find a previously initialised Like interaction

                                            await self.send(text_data=json.dumps({
                                                'message_id' : message_id,
                                                'action' : 'unlike',
                                                'changeBy' : '1'
                                            }))

                                            await self.handle_interaction(message, puppet, 'UNLIKE')
                                            await self.channel_layer.group_send(
                                                self.post_group_name, {"type" : "message_interaction", "message_id" :  message_id, "interaction" : "unlike", "changeBy" : "1", "interacting_channel" : self.channel_name}
                                            )

                                            await self.dog_check(message)

                                        elif (await self.find_interaction(message, puppet, interaction_type=Interaction.DISLIKE)): # We find a previously initialised Dislike interaction

                                            await self.send(text_data=json.dumps({
                                                'message_id' : message_id,
                                                'action' : 'like',
                                                'changeBy' : '2'
                                            }))

                                            await self.handle_interaction(message, puppet, 'LIKE')
                                            await self.channel_layer.group_send(
                                                self.post_group_name, {"type" : "message_interaction", "message_id" :  message_id, "interaction" : "like", "changeBy" : "2", "interacting_channel" : self.channel_name}
                                            )

                                            await self.dog_check(message)

                                        else: # No previous interactions

                                            await self.send(text_data=json.dumps({
                                                'message_id' : message_id,
                                                'action' : 'like',
                                                'changeBy' : '1'
                                            }))

                                            await self.handle_interaction(message, puppet, 'LIKE')
                                            await self.channel_layer.group_send(
                                                self.post_group_name, {"type" : "message_interaction", "message_id" :  message_id, "interaction" : "like", "changeBy" : "1", "interacting_channel" : self.channel_name}
                                            )

                                            await self.dog_check(message)

                                    elif text_data_json['attempt'] == 'dislike':

                                        message = await self.find_message(message_code=message_code)

                                        if await self.find_interaction(message, puppet, interaction_type=Interaction.DISLIKE):

                                            await self.find_interaction(message, puppet, interaction_type=Interaction.DISLIKE)
                                            await self.send(text_data=json.dumps({
                                                'message_id' : message_id,
                                                'action' : 'undislike',
                                                'changeBy' : '1',
                                            }))
                                            await self.handle_interaction(message, puppet, 'UNDISLIKE')
                                            await self.channel_layer.group_send(
                                                self.post_group_name, {"type" : "message_interaction", "message_id" :  message_id, "interaction" : "undislike", "changeBy" : "1", "interacting_channel" : self.channel_name}
                                            )

                                            await self.dog_check(message)

                                        elif await self.find_interaction(message, puppet, interaction_type=Interaction.LIKE):

                                            await self.send(text_data=json.dumps({
                                                'message_id' : message_id,
                                                'action' : 'dislike',
                                                'changeBy' : '2',
                                            }))
                                            await self.handle_interaction(message, puppet, 'DISLIKE')
                                            await self.channel_layer.group_send(
                                                self.post_group_name, {"type" : "message_interaction", "message_id" :  message_id, "interaction" : "dislike", 'changeBy' : "2", "interacting_channel" : self.channel_name}
                                            )

                                            await self.dog_check(message)
                                        
                                        else:
                                            
                                            await self.send(text_data=json.dumps({
                                                'message_id' : message_id,
                                                'action' : 'dislike',
                                                'changeBy' : '1',
                                            }))
                                            await self.handle_interaction(message, puppet, 'DISLIKE')
                                            await self.channel_layer.group_send(
                                                self.post_group_name, {"type" : "message_interaction", "message_id" :  message_id, "interaction" : "dislike", 'changeBy' : "1", "interacting_channel" : self.channel_name}
                                            )

                                            await self.dog_check(message)
                            else:

                                if message_author != user:

                                    if text_data_json['attempt'] == 'like':

                                        if (await self.find_interaction(message, user, interaction_type=Interaction.LIKE)):

                                            await self.send(text_data=json.dumps({
                                                'message_id' : message_id,
                                                'action' : 'unlike',
                                                'changeBy' : '1'
                                            }))

                                            await self.handle_interaction(message, user, 'UNLIKE')
                                            await self.channel_layer.group_send(
                                                self.post_group_name, {"type" : "message_interaction", "message_id" :  message_id, "interaction" : "unlike", "changeBy" : "1", "interacting_channel" : self.channel_name}
                                            )

                                            await self.dog_check(message)

                                        elif (await self.find_interaction(message, user, interaction_type=Interaction.DISLIKE)):

                                            await self.send(text_data=json.dumps({
                                                'message_id' : message_id,
                                                'action' : 'like',
                                                'changeBy' : '2',
                                            }))

                                            await self.handle_interaction(message, user, 'LIKE')
                                            await self.channel_layer.group_send(
                                                self.post_group_name, {"type" : "message_interaction", "message_id" :  message_id, "interaction" : "like", "changeBy" : "2", "interacting_channel" : self.channel_name}
                                            )

                                            await self.dog_check(message)

                                        else:

                                            await self.send(text_data=json.dumps({
                                                'message_id' : message_id,
                                                'action' : 'like',
                                                'changeBy' : '1'
                                            }))

                                            await self.handle_interaction(message, user, 'LIKE')
                                            await self.channel_layer.group_send(
                                                self.post_group_name, {"type" : "message_interaction", "message_id" :  message_id, "interaction" : "like", "changeBy" : "1", "interacting_channel" : self.channel_name}
                                            )

                                            await self.dog_check(message)

                                    elif text_data_json['attempt'] == 'dislike':

                                        message = await self.find_message(message_code=message_code)

                                        if await self.find_interaction(message, user, interaction_type=Interaction.DISLIKE):

                                            await self.find_interaction(message, user, interaction_type=Interaction.DISLIKE)
                                            await self.send(text_data=json.dumps({
                                                'message_id' : message_id,
                                                'action' : 'undislike',
                                                'changeBy' : '1'
                                            }))

                                            await self.handle_interaction(message, user, 'UNDISLIKE')
                                            await self.channel_layer.group_send(
                                                self.post_group_name, {"type" : "message_interaction", "message_id" :  message_id, "interaction" : "undislike", "changeBy" : "1", "interacting_channel" : self.channel_name}
                                            )

                                            await self.dog_check(message)
                                        
                                        elif (await self.find_interaction(message, user, interaction_type=Interaction.LIKE)):

                                            await self.send(text_data=json.dumps({
                                                'message_id' : message_id,
                                                'action' : 'dislike',
                                                'changeBy' : '2'
                                            }))

                                            await self.handle_interaction(message, user, 'DISLIKE')
                                            await self.channel_layer.group_send(
                                                self.post_group_name, {"type" : "message_interaction", "message_id" :  message_id, "interaction" : "dislike", "changeBy" : "2", "interacting_channel" : self.channel_name}
                                            )

                                            await self.dog_check(message)

                                        else:

                                            await self.send(text_data=json.dumps({
                                                'message_id' : message_id,
                                                'action' : 'dislike',
                                                'changeBy' : '1'
                                            }))
                                            await self.handle_interaction(message, user, 'DISLIKE')
                                            await self.channel_layer.group_send(
                                                self.post_group_name, {"type" : "message_interaction", "message_id" :  message_id, "interaction" : "dislike", "changeBy" : "1", "interacting_channel" : self.channel_name}
                                            )

                                            await self.dog_check(message)

            elif 'message' in text_data_json.keys():

                if user.is_authenticated:

                    message = re.sub(r'\n+', '\n', text_data_json["message"]).strip()
                    
                    if message:

                        if 'puppet' in text_data_json.keys() and user.is_superuser:
                            
                            puppet_name = text_data_json["puppet"]

                            puppet = await self.get_user(puppet_name)

                            if puppet.color == 'DR':
                                is_walker = True
                            else:
                                is_walker = False

                            if not message.startswith('/'):

                                if len(message) <= 1000:

                                    await self.handle_engage(puppet)
                                    await self.handle_active(puppet)

                                    if not await self.contrib_check(puppet):

                                        await self.channel_layer.group_send(
                                            self.post_group_name, {"type" : "add_contrib", "contrib_user" :  puppet.display_name, 'contrib_color' : puppet.color}
                                        )

                                    new_message = await self.log_message(message, puppet)

                                    if '@' in message:

                                        mention_data_string = ""
                                        
                                        mentionTuples = re.findall("(^|[^@\w])@(\w{1,20})", message)

                                        for mentionTuple in mentionTuples:
                                            mentioned_user = await self.get_user(mentionTuple[1])

                                            if mentioned_user:
                                                mention_data_string += f"{mentioned_user.display_name},{mentioned_user.color},"
                                            else:
                                                mention_data_string += f"{mentionTuple[1]},OR,"

                                        # Send message to post group
                                        await self.channel_layer.group_send(
                                            self.post_group_name, {"type" : "chat_message", "message_code" :  new_message.message_code, "message" : new_message.message_content, "author_name" : new_message.message_author_name, "author_color" : new_message.message_author.color, "sending_channel" : self.channel_name, "mention_data_string" : mention_data_string, "is_walker" : is_walker, "is_anon" : False}
                                        )

                                    else:

                                        # Send message to post group
                                        await self.channel_layer.group_send(
                                            self.post_group_name, {"type" : "chat_message", "message_code" :  new_message.message_code, "message" : new_message.message_content, "author_name" : new_message.message_author_name, "author_color" : new_message.message_author.color, "sending_channel" : self.channel_name, "is_walker" : is_walker, "is_anon" : False}
                                        )
                                    
                                        await self.channel_layer.group_send(
                                            'main',
                                            {
                                                'type': 'update_post',
                                                "post_code" : self.post_code,
                                                "last_message_content" : message,
                                            }
                                        ) 

                                    await self.notify() # Notify the users of a new message

                                else:

                                    await self.send(text_data=json.dumps({
                                        "alert" : "message_error",
                                        "message" : result,
                                    }))

                            else:

                                result = await self.handle_command(message, puppet)

                                await self.send(text_data=json.dumps({
                                    "alert" : "command_success",
                                    "message" : result,
                                }))

                        else:

                            if not message.startswith('/'):

                                if len(message) <= 1000:

                                    if not await self.ban_check(user):
                                    
                                        await self.handle_engage(user)
                                        await self.handle_active(user)

                                        if user.color == 'DR':
                                            is_walker = True
                                        else:
                                            is_walker = False

                                        if not await self.contrib_check(user):

                                            await self.channel_layer.group_send(
                                                self.post_group_name, {"type" : "add_contrib", "contrib_user" :  user.display_name, 'contrib_color' : user.color}
                                            )

                                        new_message = await self.log_message(message, user)

                                        if '@' in message:

                                            mention_data_string = ""
                                            
                                            mentionTuples = re.findall("(^|[^@\w])@(\w{1,20})", message)

                                            for mentionTuple in mentionTuples:
                                                mentioned_user = await self.get_user(mentionTuple[1])

                                                if mentioned_user:
                                                    mention_data_string += f"{mentioned_user.display_name},{mentioned_user.color},"
                                                else:
                                                    mention_data_string += f"{mentionTuple[1]},OR,"

                                            # Send message to post group
                                            await self.channel_layer.group_send(
                                                self.post_group_name, {"type" : "chat_message", "message_code" :  new_message.message_code, "message" : new_message.message_content, "author_name" : new_message.message_author_name, "author_color" : new_message.message_author.color, "sending_channel" : self.channel_name, "mention_data_string" : mention_data_string, "is_walker" : is_walker, "is_anon" : False}
                                            )

                                        else:
                                            
                                            # Send message to post group
                                            await self.channel_layer.group_send(
                                                self.post_group_name, {"type" : "chat_message", "message_code" :  new_message.message_code, "message" : new_message.message_content, "author_name" : new_message.message_author_name, "author_color" : new_message.message_author.color, "sending_channel" : self.channel_name, "is_walker" : is_walker, "is_anon" : False}
                                            )

                                        await self.channel_layer.group_send(
                                            'main',
                                            {
                                                'type': 'update_post',
                                                "post_code" : self.post_code,
                                                "last_message_content" : message,
                                            }
                                        )

                                        await self.notify() # Notify the users of a new message
                                        
                                    else:

                                        await self.send(text_data=json.dumps({
                                            "message_code" : get_random_string(length=12),
                                            "message" : message,
                                            "author" : user.display_name,
                                            "author_color" : user.color,
                                            "origin" : "native",
                                        }))

                                else:

                                    await self.send(text_data=json.dumps({
                                        "alert" : "message_failure",
                                        "message" : "That message goes over 1000 characters. Just shorten it down or split it up to send it properly.",
                                    }))

                            else:

                                result = await self.handle_command(message, user)

                                await self.send(text_data=json.dumps({
                                    "alert" : "command_success",
                                    "message" : result,
                                }))
                else:

                    message = re.sub(r'\n+', '\n', text_data_json["message"]).strip()
                    
                    if message:

                        if len(message) <= 500:

                            new_message = await self.log_message(message, None)

                            is_walker = False

                            if '@' in message:

                                mention_data_string = ""
                                
                                mentionTuples = re.findall("(^|[^@\w])@(\w{1,20})", message)

                                for mentionTuple in mentionTuples:
                                    mentioned_user = await self.get_user(mentionTuple[1])

                                    if mentioned_user:
                                        mention_data_string += f"{mentioned_user.display_name},{mentioned_user.color},"
                                    else:
                                        mention_data_string += f"{mentionTuple[1]},OR,"

                                # Send message to post group
                                await self.channel_layer.group_send(
                                    self.post_group_name, {"type" : "chat_message", "message_code" :  new_message.message_code, "message" : new_message.message_content, "author_name" : "Anon", "author_color" : "OR", "sending_channel" : self.channel_name, "mention_data_string" : mention_data_string, "is_walker" : is_walker, "is_anon" : True}
                                )

                            else:
                                
                                # Send message to post group
                                await self.channel_layer.group_send(
                                    self.post_group_name, {"type" : "chat_message", "message_code" :  new_message.message_code, "message" : new_message.message_content, "author_name" : "Anon", "author_color" : "OR", "sending_channel" : self.channel_name, "is_walker" : is_walker, "is_anon" : True}
                                )

                            await self.channel_layer.group_send(
                                'main',
                                {
                                    'type': 'update_post',
                                    "post_code" : self.post_code,
                                    "last_message_content" : message,
                                }
                            ) 

                            await self.notify() # Notify the users of a new message

                        else:

                            await self.send(text_data=json.dumps({
                                "alert" : "message_failure",
                                "message" : "That message goes over 100 characters. Make a profile to send more",
                            }))


            elif 'voting' in text_data_json.keys():
                user = self.scope["user"]
                
                post = await self.get_post()

                if post.post_type != 'QU':

                    if 'puppet' in text_data_json.keys() and user.is_superuser:

                        puppet_name = text_data_json["puppet"]

                        puppet = await self.get_user(puppet_name)

                        vote = text_data_json["voting"]

                        if vote == 'N':

                            await self.handle_vote('N', puppet)

                            tally = await self.tally_votes()

                            await self.channel_layer.group_send(
                                self.post_group_name, {"type" : "update_vote", "y_votes" :  tally['y'], "n_votes" : tally['n']}
                            )

                        elif vote == 'Y':

                            await self.handle_vote('Y', puppet)

                            tally = await self.tally_votes()

                            await self.channel_layer.group_send(
                                self.post_group_name, {"type" : "update_vote", "y_votes" :  tally['y'], "n_votes" : tally['n']}
                            )

                    elif user.is_authenticated:

                        vote = text_data_json["voting"]

                        if vote == 'N':

                            await self.handle_vote('N', self.scope["user"])

                            tally = await self.tally_votes()

                            await self.channel_layer.group_send(
                                self.post_group_name, {"type" : "update_vote", "y_votes" :  tally['y'], "n_votes" : tally['n']}
                            )

                        elif vote == 'Y':

                            await self.handle_vote('Y', self.scope["user"])

                            tally = await self.tally_votes()

                            await self.channel_layer.group_send(
                                self.post_group_name, {"type" : "update_vote", "y_votes" :  tally['y'], "n_votes" : tally['n']}
                            )
                    else:
                        await self.send(text_data=json.dumps({
                            "redirect" : "/create-profile/",
                        }))

            elif 'ping' in text_data_json.keys():

                if text_data_json['ping'] == 'performance':
                        await self.send(text_data=json.dumps({
                            'pong' : 'performance',
                        }))

                elif text_data_json['ping'] == 'initial':

                    if user.is_authenticated:

                        await self.denotify(user)

            elif 'online_status' in text_data_json.keys():

                if text_data_json["online_status"] == "online":

                    if user.is_superuser:
                            
                        try:
                            
                            #puppets = ['Turnabout', 'Twizzerty', 'tom', 'Cruz', 'Fishnivore', 'MUSCLEman', 'aidenm', 'Too2Turbo', 'SkrillFalcon', 'cupcake_sparkles34', 'bobgoodman', 'TobiasW', 'arealchimpanzee', 'spike', 'righthook23', 'Dragonstrix', '_andwhitecat', 'Hazad456', 'TorScore', 'jamie', 'chimpster', 'ChrissyTubs', 'narayan IISC', 'Naramora']

                            puppets = ['Turnabout', 'Twizzerty', 'tom']

                            for puppet_name in puppets:

                                puppet_model = await self.get_user(puppet_name)

                                await self.channel_layer.group_send(
                                    self.post_group_name, {"type" : "online_alert", "online_user" :  puppet_model.display_name, "online_color" : puppet_model.color, "online_status" : "online", "online_timestamp" : text_data_json["online_timestamp"]}
                                )

                        except:

                            puppets = ['aidenm', 'billybob', 'skrill_falcon_blast', 'GameTheory']

                            for puppet_name in puppets:

                                puppet_model = await self.get_user(puppet_name)

                                await self.channel_layer.group_send(
                                    self.post_group_name, {"type" : "online_alert", "online_user" :  puppet_model.display_name, "online_color" : puppet_model.color, "online_status" : "online", "online_timestamp" : text_data_json["online_timestamp"]}
                                )
                    

                    elif user.is_authenticated:

                        await self.channel_layer.group_send(
                            self.post_group_name, {"type" : "online_alert", "online_user" :  user.display_name, "online_color" : user.color, "online_status" : "online", "online_timestamp" : text_data_json["online_timestamp"]}
                        )

                    else:
                        await self.channel_layer.group_send(
                            self.post_group_name, {"type" : "online_alert", "online_user" :  f'Anon{self.channel_name}', "online_color" : 'OR', "online_status" : "online", "online_timestamp" : text_data_json["online_timestamp"]}
                        )

            elif 'typing_status' in text_data_json.keys():
                
                if user.is_authenticated:

                    if text_data_json["typing_status"] == 'started':

                        if 'puppet' in text_data_json.keys() and user.is_superuser:

                            puppet_name = text_data_json["puppet"]

                            puppet = await self.get_user(puppet_name)

                            await self.channel_layer.group_send(
                                self.post_group_name, {"type" : "typing_alert", "typing_display_name" :  puppet.display_name, "typing_color" : puppet.color, "typing_status" : "started", "typing_channel" : self.channel_name}
                            )
                            
                            await self.channel_layer.group_send(
                                'main',
                                {
                                    'type': 'someone_typing',
                                    "post_code" : self.post_code,
                                }
                            ) 

                        else:

                            await self.channel_layer.group_send(
                                self.post_group_name, {"type" : "typing_alert", "typing_display_name" :  user.display_name, "typing_color" : user.color, "typing_status" : "started", "typing_channel" : self.channel_name}
                            )

                            await self.channel_layer.group_send(
                                'main',
                                {
                                    'type': 'someone_typing',
                                    "post_code" : self.post_code,
                                }
                            ) 
                    
                    if text_data_json["typing_status"] == 'stopped':

                        if 'puppet' in text_data_json.keys() and user.is_superuser:

                            puppet_name = text_data_json["puppet"]

                            puppet = await self.get_user(puppet_name)

                            await self.channel_layer.group_send(
                                self.post_group_name, {"type" : "typing_alert", "typing_display_name" :  puppet.display_name, "typing_color" : puppet.color, "typing_status" : "stopped", "typing_channel" : self.channel_name}
                            )
                        else:
                            await self.channel_layer.group_send(
                                self.post_group_name, {"type" : "typing_alert", "typing_display_name" :  user.display_name, "typing_color" : user.color, "typing_status" : "stopped", "typing_channel" : self.channel_name}
                            )

            elif 'edit' in text_data_json.keys():

                if user.is_authenticated:

                    if 'puppet' in text_data_json.keys() and user.is_superuser:

                        puppet_name = text_data_json["puppet"]

                        puppet = await self.get_user(puppet_name)

                        message_id = text_data_json["message_id"]
                        message_code = message_id[4:]

                        edited_message = re.sub(r'\n+', '\n', text_data_json["edit"]).strip()

                        if edited_message:

                            edited_message = await self.edit_message(message_code, edited_message, puppet) # The function verifies if the message author and the editing author are identical.

                            if edited_message:

                                if '@' in edited_message.message_content:

                                    mention_data_string = ""
                                    
                                    mentionTuples = re.findall("(^|[^@\w])@(\w{1,20})", edited_message.message_content)

                                    for mentionTuple in mentionTuples:
                                        mentioned_user = await self.get_user(mentionTuple[1])

                                        if mentioned_user:
                                            mention_data_string += f"{mentioned_user.display_name},{mentioned_user.color},"
                                        else:
                                            mention_data_string += f"{mentionTuple[1]},OR,"

                                    # Send message to post group

                                    await self.channel_layer.group_send(
                                        self.post_group_name, {"type" : "chat_message_edit", "message_code" :  edited_message.message_code, "edited_content" : edited_message.message_content, "mention_data_string" : mention_data_string}
                                    )

                                else:

                                    # Send message to post group
                                    await self.channel_layer.group_send(
                                        self.post_group_name, {"type" : "chat_message_edit", "message_code" :  edited_message.message_code, "edited_content" : edited_message.message_content}
                                    )

                        else: # On an empty edit, find the orignal message and simply replace the original data. This is sent only to the editors screen to rectify their failed edit.
            
                            original_message = await self.find_message(message_code=message_code)

                            await self.send(text_data=json.dumps({
                                "message_code" : message_code,
                                "edited_content" : original_message.message_content,
                            }))
                    else:

                        message_id = text_data_json["message_id"]
                        message_code = message_id[4:]

                        edited_message = re.sub(r'\n+', '\n', text_data_json["edit"]).strip()

                        if edited_message:

                            edited_message = await self.edit_message(message_code, edited_message, user) # The function verifies if the message author and the editing author are identical.

                            if edited_message:

                                if '@' in edited_message.message_content:

                                    mention_data_string = ""
                                    
                                    mentionTuples = re.findall("(^|[^@\w])@(\w{1,20})", edited_message.message_content)

                                    for mentionTuple in mentionTuples:
                                        mentioned_user = await self.get_user(mentionTuple[1])

                                        if mentioned_user:
                                            mention_data_string += f"{mentioned_user.display_name},{mentioned_user.color},"
                                        else:
                                            mention_data_string += f"{mentionTuple[1]},OR,"

                                    # Send message to post group

                                    await self.channel_layer.group_send(
                                        self.post_group_name, {"type" : "chat_message_edit", "message_code" :  edited_message.message_code, "edited_content" : edited_message.message_content, "mention_data_string" : mention_data_string}
                                    )

                                else:

                                    # Send message to post group
                                    await self.channel_layer.group_send(
                                        self.post_group_name, {"type" : "chat_message_edit", "message_code" :  edited_message.message_code, "edited_content" : edited_message.message_content}
                                    )

                        else: # On an empty edit, find the orignal message and simply replace the original data. This is sent only to the editors screen to rectify their failed edit.
            
                            original_message = await self.find_message(message_code=message_code)

                            await self.send(text_data=json.dumps({
                                "message_code" : message_code,
                                "edited_content" : original_message.message_content,
                            }))

            elif 'reconnecting' in text_data_json.keys():
                
                message_id = text_data_json['last_message_id']
                message_code = message_id[4:] # Get the message code without the 'msg_' part

                unloaded_messages = await self.get_unloaded_messages(message_code=message_code)

                async for message in unloaded_messages:
                    message_author = await self.get_author(message)

                    if message_author:

                        if user.color == 'DR':
                            is_walker = True
                        else:
                            is_walker = False

                        if message_author == user:
                            await self.send(text_data=json.dumps({
                                "message_code" : message_code,
                                "message" : message.message_content,
                                "author" : message.message_author.display_name,
                                "author_color" : message.message_author.color,
                                "is_walker" : str(is_walker),
                                "origin" : "native",
                            }))
                        else:
                            await self.send(text_data=json.dumps({
                                "message_code" : message_code,
                                "message" : message.message_content,
                                "author" : message.message_author.display_name,
                                "author_color" : message.message_author.color,
                                "is_walker" : str(is_walker),
                                "origin" : "foreign",
                            }))

                    else:
                        is_walker = False

                        await self.send(text_data=json.dumps({
                            "message_code" : message_code,
                            "message" : message.message_content,
                            "author" : 'Anon',
                            "author_color" : 'OR',
                            "is_walker" : str(is_walker),
                            "origin" : "foreign",
                        }))
        elif bytes_data and not text_data:

            # A duck test for the data to check if the data is in byte form.
            
            try:

                decoded_data = bytes_data.decode() # Converting to a string

                data = json.loads(decoded_data) # Parsing into dictionary

                if data['message']:

                    message = re.sub(r'\n+', '\n', data["message"]).strip()
                    
                    if message:

                        if len(message) <= 500:

                            new_message = await self.log_message(message, None)

                            is_walker = False

                            await self.channel_layer.group_send(
                                self.post_group_name, {"type" : "chat_message", "message_code" :  new_message.message_code, "message" : new_message.message_content, "author_name" : "Anon", "author_color" : "OR", "sending_channel" : self.channel_name, "is_walker" : is_walker, "is_anon" : True}
                            )

                            await self.channel_layer.group_send(
                                'main',
                                {
                                    'type': 'update_post',
                                    "post_code" : self.post_code,
                                    "last_message_content" : message,
                                }
                            ) 

                            await self.notify() # Notify the users of a new message
                
            except UnicodeDecodeError as e:

                print('UnicodeDecodeError: ', e)

            except AttributeError as e:
                
                print('AttributeError: ', e)



    # Receive message from post group
    async def chat_message(self, event):
        message_code = event["message_code"]
        message = event["message"]
        author_name = event["author_name"]
        color = event["author_color"]
        is_walker = event["is_walker"]
        is_anon = event["is_anon"]

        sending_channel = event["sending_channel"]

        user = self.scope["user"]

        try:
            mention_data_string = event["mention_data_string"]
        except:
            mention_data_string = ''


        if user.is_authenticated:
            await self.denotify(user)

        # Send message to WebSocket
        if self.channel_name == sending_channel and author_name != 'Anon':
            await self.send(text_data=json.dumps({
                "message_code" : message_code,
                "message" : message,
                "author" : author_name,
                "author_color" : color,
                "origin" : "native",
                "mention_data_string" : mention_data_string,
                "is_walker" : str(is_walker)
                }))
        else:
            await self.send(text_data=json.dumps({
                "message_code" : message_code,
                "message" : message,
                "author" : author_name,
                "author_color" : color,
                "origin" : "foreign",
                "mention_data_string" : mention_data_string,
                "is_walker" : str(is_walker)
                }))
        
    async def message_interaction(self, event):
        message_id = event["message_id"]
        interaction = event["interaction"]
        interacting_channel = event["interacting_channel"]
        changeBy = event["changeBy"]

        if self.channel_name != interacting_channel:
            await self.send(text_data=json.dumps({
                "message_id" : message_id,
                "interaction" : interaction,
                "changeBy" : changeBy
            }))

    async def typing_alert(self, event):
        typing_user = event["typing_display_name"]
        typing_color = event["typing_color"]
        typing_status = event["typing_status"]

        typing_channel = event["typing_channel"]

        if self.channel_name != typing_channel:
            await self.send(text_data=json.dumps({
                "typing_user" : typing_user,
                "typing_color" : typing_color,
                "typing_status" : typing_status
            }))
    
    async def online_alert(self, event):
        online_user = event["online_user"]
        online_color = event["online_color"]
        online_status = event["online_status"]
        online_timestamp = event["online_timestamp"]

        await self.send(text_data=json.dumps({
            "online_user" : online_user,
            "online_color" : online_color,
            "online_status" : online_status,
            "online_timestamp" : online_timestamp
        }))

    async def add_contrib(self, event):
        contrib_user = event["contrib_user"]
        contrib_color = event["contrib_color"]

        await self.send(text_data=json.dumps({
            "contrib_user" : contrib_user,
            "contrib_color" : contrib_color,
        }))

    async def update_vote(self, event):
        y_votes= event["y_votes"]
        n_votes = event["n_votes"]

        await self.send(text_data=json.dumps({
            "y_votes" : y_votes,
            "n_votes" : n_votes,
        }))

    async def chat_message_edit(self, event):
        message_code = event["message_code"]
        edited_content = event["edited_content"]

        try:
            mention_data_string = event["mention_data_string"]
        except:
            mention_data_string = ''

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
                "message_code" : message_code,
                "edited_content" : edited_content,
                "mention_data_string" : mention_data_string,
            }))
