from django.core.management.base import BaseCommand, CommandError
from delivery.views import getDeliveryListByDate
import pytz
import subprocess
from django.utils import timezone
from datetime import datetime, timedelta, time
from users.views import getEndBalanceOfMonth, last_day_of_month
from users.models import Staff, Purchase, Product, ExtraLess, Vacation, Subscription, UserType, User
from django.db.models import Q

class Command(BaseCommand):
    help = 'Update purchase amount from a date'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def add_arguments(self, parser):
        parser.add_argument('date', type=str)

    def handle(self, *args, **options):

        date = datetime.strptime(options['date'], '%Y-%m-%d').replace(tzinfo=pytz.UTC)

        date_min = datetime.combine(date, time.min)
        date_max = datetime.combine(date, time.max)
        
        purchase = Purchase.objects.filter(date__range=(date_min, date_max)).order_by('-date', '-id')

        for p in purchase:

            product = Product.objects.get(id=1)
            amount = float(product.price + p.user.user_type.price_variation) * float(p.quantity)

            p.amount = amount
            p.save()
            print(p.id)
