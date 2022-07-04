# Generated by Django 3.2.3 on 2022-03-11 04:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_auto_20220311_0931'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacation',
            name='created_by',
            field=models.CharField(choices=[('customer', 'Customer'), ('admin', 'Admin'), ('manager', 'Manager')], default='admin', max_length=50),
        ),
        migrations.AlterField(
            model_name='vacation',
            name='edited_by',
            field=models.CharField(choices=[('customer', 'Customer'), ('admin', 'Admin'), ('manager', 'Manager')], default='admin', max_length=50),
        ),
    ]
