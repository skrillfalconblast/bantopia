# Generated by Django 4.2.2 on 2023-07-15 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0010_alter_interaction_interaction_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interaction',
            name='interaction_datetime',
            field=models.DateTimeField(auto_now=True, verbose_name='date and time of the like'),
        ),
    ]