# Generated by Django 3.2.3 on 2022-02-22 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0002_alter_deliverydata_is_extra'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deliverydata',
            name='quantity',
        ),
        migrations.AddField(
            model_name='deliverydata',
            name='packet',
            field=models.IntegerField(default=None),
            preserve_default=False,
        ),
    ]
