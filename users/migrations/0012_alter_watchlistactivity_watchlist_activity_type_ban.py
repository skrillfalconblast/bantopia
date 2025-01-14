# Generated by Django 4.2.2 on 2023-09-12 16:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_remove_user_date_joined_user_datetime_joined'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watchlistactivity',
            name='watchlist_activity_type',
            field=models.CharField(choices=[('ACTIVE', 'Active'), ('DECLARE', 'Declare'), ('THEORISE', 'Theorise'), ('ASK', 'Ask'), ('ENGAGE', 'Engage'), ('POPULAR', 'Popular'), ('INFAMOUS', 'Infamous'), ('CONTROVERSIAL', 'Controversial')], max_length=255),
        ),
        migrations.CreateModel(
            name='Ban',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('banned_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
