# Generated by Django 4.2.2 on 2023-07-19 20:30

from django.db import migrations, models
import posts.models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_post_post_timestamp_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='post_number_of_no_votes',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='post_number_of_yes_votes',
            field=models.IntegerField(default=0),
        ),
    ]