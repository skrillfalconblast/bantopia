# Generated by Django 4.2.2 on 2023-07-21 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0011_visit'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='post_tags',
            field=models.ManyToManyField(to='posts.tag'),
        ),
    ]
