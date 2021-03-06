# Generated by Django 3.2.3 on 2021-11-30 14:15

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_user_email'),
        ('collection', '0003_auto_20211129_1915'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collection',
            name='verified',
        ),
        migrations.AddField(
            model_name='collection',
            name='payment',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='users.payment', verbose_name='payment data'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='collection',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 30, 14, 14, 36, 273132, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='expenses',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 30, 14, 14, 36, 291333, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='handover',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 30, 14, 14, 36, 290518, tzinfo=utc)),
        ),
    ]
