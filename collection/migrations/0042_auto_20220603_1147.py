# Generated by Django 3.2.3 on 2022-06-03 06:17

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0041_auto_20220603_1008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 3, 6, 17, 59, 61073, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='expenses',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 3, 6, 17, 59, 80099, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='handover',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 3, 6, 17, 59, 79559, tzinfo=utc)),
        ),
    ]
