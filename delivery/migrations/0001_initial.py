# Generated by Django 3.2.3 on 2022-02-07 11:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0011_remove_staff_manager'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryData',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=20)),
                ('order', models.IntegerField()),
                ('is_extra', models.BooleanField()),
                ('date', models.DateField(auto_now_add=True)),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.route', verbose_name='delivery route')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user', verbose_name='assigned user')),
            ],
        ),
    ]
