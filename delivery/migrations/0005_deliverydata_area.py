# Generated by Django 3.2.3 on 2022-06-03 06:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0022_auto_20220311_1024'),
        ('delivery', '0004_auto_20220603_1008'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliverydata',
            name='area',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.area', verbose_name='delivery area'),
        ),
    ]
