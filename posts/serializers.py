from rest_framework import serializers

from .models import Post
from chat.models import Message

from django.db.models import prefetch_related_objects

class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    recent_messages = serializers.SerializerMethodField(read_only=True)

    def get_recent_messages(self, obj):
        post = obj
        prefetched_post = Post.objects.prefetch_related('message_set').get(pk=post.pk)
        post_recent_messages = prefetched_post.message_set.all().prefetch_related('message_mentions').order_by('-message_datetime_sent')[:1000:-1]
        return MessageSerializer(post_recent_messages, many=True).data
    

    class Meta:
        model = Post
        fields = [
            'post_code',
            'post_type',
            'post_title',
            'post_desc',

            'post_author',
            'post_author_name',

            'post_TPP',
            'post_PEN1',

            'post_datetime_created',
            'post_number_of_messages',
            'post_timestamp_created',

            'post_number_of_yes_votes',
            'post_number_of_no_votes',

            'post_slug',
            
            'notified',

            'recent_messages'
        ]