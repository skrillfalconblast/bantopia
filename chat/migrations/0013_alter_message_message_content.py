# Generated by Django 4.2.2 on 2023-08-21 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0012_alter_message_message_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='message_content',
            field=models.TextField(),
        ),
    ]
