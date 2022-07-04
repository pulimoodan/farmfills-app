from django.core.management.base import BaseCommand, CommandError
from delivery.views import getDeliveryListByDate
import pytz
import subprocess
from django.utils import timezone
from datetime import datetime, timedelta
from delivery.views import getDeliveryList
from users.models import Route
from delivery.models import DeliveryData
from dispatch.views import getBulkCusomersOrder

class Command(BaseCommand):
    help = 'Generate delivery data for each day'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle(self, *args, **options):
        routes = Route.objects.all().exclude(id=1)
        total = 0

        for route in routes: 
            deliveryList = getDeliveryList(route)
            for idx, l in enumerate(deliveryList['list']):
                deliveryData = DeliveryData(user=l['user'], packet=l['packet'], order=idx, route=route)
                deliveryData.save()
            for idx, l in enumerate(deliveryList['assigned']):
                deliveryData = DeliveryData(user=l['user'], packet=l['packet'], order=idx, is_extra=True, route=route)
                deliveryData.save()
            total += deliveryList['total']
            self.stdout.write(self.style.SUCCESS(route.name + ': ' + str(deliveryList['total']) + ' packets'))
        
        bulkOrders = getBulkCusomersOrder(timezone.localtime(timezone.now()).date())
        for idx, l in enumerate(bulkOrders['list']):
            deliveryData = DeliveryData(user=l['user'], packet=l['total'], order=idx, bulk=True, area=l['user'].area)
            deliveryData.save()
        total += bulkOrders['total']
        self.stdout.write(self.style.SUCCESS('Bulk Orders: ' + str(bulkOrders['total']) + ' packets'))

        print(timezone.localtime(timezone.now()).strftime('%d %b, %Y') + ': Successfully created delivery data: Packets = ' + str(total))
