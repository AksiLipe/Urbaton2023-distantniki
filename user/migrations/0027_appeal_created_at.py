# Generated by Django 4.2.5 on 2023-11-26 02:20

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0026_alter_news_short_description_alter_news_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='appeal',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 11, 26, 2, 20, 24, 743549, tzinfo=datetime.timezone.utc)),
        ),
    ]