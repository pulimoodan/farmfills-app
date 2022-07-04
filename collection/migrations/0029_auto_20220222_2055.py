# Generated by Django 3.2.3 on 2022-02-22 15:25

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0028_auto_20220222_2055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 2, 22, 15, 25, 7, 525157, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='expenses',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 2, 22, 15, 25, 7, 546623, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='handover',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 2, 22, 15, 25, 7, 546096, tzinfo=utc)),
        ),
    ]