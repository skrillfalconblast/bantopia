# Generated by Django 4.2.2 on 2023-08-19 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0013_remove_post_post_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='post_slug',
            field=models.SlugField(default='post'),
        ),
    ]
