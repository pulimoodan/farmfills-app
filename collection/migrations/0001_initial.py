# Generated by Django 3.2.3 on 2021-11-26 06:23

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0007_alter_user_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField(default=datetime.datetime(2021, 11, 26, 6, 23, 53, 371882, tzinfo=utc))),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('verified', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user', verbose_name='payment user')),
            ],
        ),
    ]
