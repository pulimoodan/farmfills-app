# Generated by Django 3.2.3 on 2021-06-15 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20210608_1550'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='sub_type',
            field=models.CharField(choices=[('daily', 'Daily'), ('alternate', 'Alternate'), ('weekly', 'Weekly'), ('custom', 'Custom Interval')], default='daily', max_length=50),
            preserve_default=False,
        ),
    ]
