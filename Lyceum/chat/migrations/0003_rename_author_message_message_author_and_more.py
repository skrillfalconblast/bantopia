# Generated by Django 4.2.2 on 2023-07-04 20:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_draft_draft_code'),
        ('chat', '0002_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='author',
            new_name='message_author',
        ),
        migrations.RenameField(
            model_name='message',
            old_name='text',
            new_name='message_content',
        ),
        migrations.RenameField(
            model_name='message',
            old_name='datetime_sent',
            new_name='message_datetime_sent',
        ),
        migrations.RemoveField(
            model_name='message',
            name='author_name',
        ),
        migrations.RemoveField(
            model_name='message',
            name='chat',
        ),
        migrations.AddField(
            model_name='message',
            name='messagae_author_name',
            field=models.CharField(default='enter_name', max_length=20, verbose_name='display name of author'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='message',
            name='message_post',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='posts.post'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Chat',
        ),
    ]
