# Generated by Django 3.2.3 on 2022-02-07 11:53

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0009_auto_20220207_1722'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 2, 7, 11, 53, 19, 563752, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='expenses',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 2, 7, 11, 53, 19, 582747, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='handover',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 2, 7, 11, 53, 19, 582228, tzinfo=utc)),
        ),
    ]
