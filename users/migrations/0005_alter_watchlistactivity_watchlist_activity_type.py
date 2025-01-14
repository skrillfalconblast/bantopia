# Generated by Django 4.2.2 on 2023-07-16 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_watchlistactivity_watchlist_activity_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watchlistactivity',
            name='watchlist_activity_type',
            field=models.CharField(choices=[('ACTIVE', 'Active'), ('DECLARE', 'Declare'), ('THEORISE', 'Theorise'), ('ENGAGE', 'Engage'), ('POPULAR', 'Popular'), ('INFAMOUS', 'Infamous'), ('CONTROVERSIAL', 'Controversial')], max_length=255),
        ),
    ]
