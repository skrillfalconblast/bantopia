# Generated by Django 4.2.2 on 2023-07-20 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0011_visit'),
        ('users', '0006_report'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='history',
            field=models.ManyToManyField(through='posts.Visit', to='posts.post'),
        ),
    ]
