# Generated by Django 3.2.3 on 2021-06-06 02:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Dispatch',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('start_time', models.TimeField(null=True)),
                ('end_time', models.TimeField(null=True)),
                ('date', models.DateField()),
                ('packets', models.DecimalField(decimal_places=2, max_digits=20)),
                ('packets_variation', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Otp',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('mobile', models.CharField(max_length=30)),
                ('otp', models.CharField(max_length=20)),
                ('ip', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
                ('uom', models.CharField(max_length=30)),
                ('price', models.DecimalField(decimal_places=2, max_digits=20)),
            ],
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
                ('code', models.CharField(max_length=20)),
                ('area', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('mobile', models.CharField(max_length=255)),
                ('address_type', models.CharField(blank=True, choices=[('house', 'House'), ('apartment', 'Apartment')], max_length=50, null=True)),
                ('house_name', models.CharField(blank=True, max_length=255, null=True)),
                ('house_no', models.CharField(blank=True, max_length=255, null=True)),
                ('street', models.CharField(blank=True, max_length=255, null=True)),
                ('landmark', models.TextField(blank=True, null=True)),
                ('apartment_name', models.CharField(blank=True, max_length=255, null=True)),
                ('tower', models.CharField(blank=True, max_length=255, null=True)),
                ('floor', models.CharField(blank=True, max_length=255, null=True)),
                ('door', models.CharField(blank=True, max_length=255, null=True)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('delivery_name', models.CharField(blank=True, max_length=255, null=True)),
                ('route_order', models.IntegerField()),
                ('payment_mode', models.CharField(choices=[('online', 'Online'), ('cash', 'Cash')], default='cleared', max_length=50)),
                ('email', models.CharField(max_length=255)),
                ('status', models.CharField(blank=True, choices=[('cleared', 'Cleared'), ('not cleared', 'Not Cleared')], max_length=50, null=True)),
                ('route', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.route', verbose_name='delivery route')),
            ],
        ),
        migrations.CreateModel(
            name='UserType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
                ('price_variation', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
                ('payment_type', models.CharField(blank=True, choices=[('prepaid', 'Prepaid'), ('postpaid', 'Postpaid')], max_length=50, null=True)),
                ('suspend', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Vacation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user', verbose_name='vacation user')),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='user_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.usertype', verbose_name='customer type'),
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('sub_type', models.CharField(blank=True, choices=[('daily', 'Daily'), ('alternate', 'Alternate'), ('weekly', 'Weekly'), ('custom', 'Custom Interval')], max_length=50, null=True)),
                ('daily_day1', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('daily_day2', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('alternate_quantity', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('custom_quantity', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('custom_interval', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('weekly_mon', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('weekly_tue', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('weekly_wed', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('weekly_thu', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('weekly_fri', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('weekly_sat', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('weekly_sun', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user', verbose_name='subscription user')),
            ],
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
                ('uname', models.CharField(max_length=30)),
                ('password', models.CharField(max_length=250)),
                ('delivery', models.BooleanField()),
                ('dispatch', models.BooleanField()),
                ('cash_collection', models.BooleanField()),
                ('follow_up', models.BooleanField()),
                ('billing', models.BooleanField()),
                ('admin', models.BooleanField()),
                ('vendor', models.BooleanField()),
                ('vehicle', models.CharField(blank=True, choices=[('bike', 'Bike'), ('scooter', 'Scooter')], max_length=50, null=True)),
                ('km', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('ip', models.CharField(blank=True, choices=[('bike', 'Bike'), ('scooter', 'Scooter')], max_length=50, null=True)),
                ('route', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.route', verbose_name='delivery route')),
            ],
        ),
        migrations.CreateModel(
            name='RouteAssign',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('from_route', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='users.route', verbose_name='assigned from route')),
                ('to_route', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='users.route', verbose_name='assigned to route')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user', verbose_name='assigned user')),
            ],
        ),
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=20)),
                ('reason', models.CharField(blank=True, choices=[('not delivered', 'Not delivered'), ('leaked', 'Leaked'), ('Spoiled', 'Spoiled')], max_length=50, null=True)),
                ('balance', models.DecimalField(decimal_places=2, max_digits=20)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.product', verbose_name='extra product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user', verbose_name='refund user')),
            ],
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=20)),
                ('balance', models.DecimalField(decimal_places=2, max_digits=20)),
                ('delivered_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.staff', verbose_name='delivery boy')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.product', verbose_name='purchase product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user', verbose_name='purchase user')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('mode', models.CharField(blank=True, choices=[('online', 'Online'), ('cash', 'Cash'), ('bank transfer', 'Bank Transfer')], max_length=50, null=True)),
                ('order_id', models.CharField(blank=True, max_length=50, null=True)),
                ('payment_id', models.CharField(blank=True, max_length=50, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('paid', models.BooleanField()),
                ('balance', models.DecimalField(decimal_places=2, max_digits=20)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user', verbose_name='payment user')),
            ],
        ),
        migrations.CreateModel(
            name='ExtraLess',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=20)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user', verbose_name='extraless user')),
            ],
        ),
        migrations.CreateModel(
            name='Extra',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=20)),
                ('note', models.TextField(blank=True, null=True)),
                ('balance', models.DecimalField(decimal_places=2, max_digits=20)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.product', verbose_name='extra product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user', verbose_name='extra user')),
            ],
        ),
        migrations.CreateModel(
            name='Delivery',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('start_time', models.TimeField(blank=True, null=True)),
                ('end_time', models.TimeField(blank=True, null=True)),
                ('dispatch_start_time', models.TimeField(blank=True, null=True)),
                ('dispatch_end_time', models.TimeField(blank=True, null=True)),
                ('date', models.DateField()),
                ('packets', models.DecimalField(decimal_places=2, max_digits=20)),
                ('packets_variation', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
                ('km', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
                ('km_variation', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
                ('delivery_boy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='users.staff', verbose_name='delivery boy')),
                ('route', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.route', verbose_name='delivery route')),
            ],
        ),
        migrations.CreateModel(
            name='BillNotification',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user', verbose_name='bill user')),
            ],
        ),
    ]
