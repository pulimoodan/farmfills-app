# Generated by Django 3.2.3 on 2022-03-11 04:25

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0034_auto_20220311_0931'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 3, 11, 4, 25, 19, 620766, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='expenses',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 3, 11, 4, 25, 19, 639336, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='handover',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 3, 11, 4, 25, 19, 638808, tzinfo=utc)),
        ),
    ]
