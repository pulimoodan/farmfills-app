# Generated by Django 3.2.3 on 2022-06-03 04:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0022_auto_20220311_1024'),
        ('delivery', '0003_auto_20220222_2007'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliverydata',
            name='bulk',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='deliverydata',
            name='route',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.route', verbose_name='delivery route'),
        ),
    ]
