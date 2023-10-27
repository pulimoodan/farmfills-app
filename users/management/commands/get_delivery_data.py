from django.core.management.base import BaseCommand, CommandError
from delivery.views import getDeliveryListByDate
import pytz
import subprocess
from django.utils import timezone
from datetime import datetime, timedelta
from delivery.views import getDeliveryList
from users.models import Route
from users.views import last_day_of_month
from delivery.models import DeliveryData
from django.db.models import Q
from dispatch.views import getBulkCusomersOrder

class Command(BaseCommand):
    help = 'Generate delivery data for each day'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument('date', type=str)

    def handle(self, *args, **options):
        date = datetime.strptime(options['date'], '%Y-%m-%d').replace(tzinfo=pytz.UTC)
        routes = Route.objects.all().exclude(id=1)
        last_day = last_day_of_month(date)
        first_day = last_day.replace(day=1)
        total = 0

        for route in routes: 
            print("[***" + route.name + "***]")
            delivery_data = DeliveryData.objects.filter(Q(route=route), Q(date__lt = last_day) | Q(date__contains = last_day.date()), Q(date__gt = first_day) | Q(date__contains = first_day.date()))
            for d in delivery_data:
                print(d.user.delivery_name + ": " +  str(d.packet))

            # self.stdout.write(self.style.SUCCESS('Bulk Orders: ' + str(bulkOrders['total']) + ' packets'))
