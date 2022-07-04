from django.core.management.base import BaseCommand, CommandError
from delivery.views import getDeliveryListByDate
import pytz
import subprocess
from django.utils import timezone
from datetime import datetime, timedelta
from users.views import getEndBalanceOfMonth, last_day_of_month
from users.models import Staff, Purchase, Product, ExtraLess, Vacation, Subscription, UserType, User
from django.db.models import Q

class Command(BaseCommand):
    help = 'Update purchase amount from a date'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle(self, *args, **options):

        # last_day = last_day_of_month(timezone.localtime(timezone.now()))

        # first_day = last_day.replace(day=1)

        # last_day = last_day.replace(day=3)

        # utype1 = UserType.objects.get(id=1)
        # utype2 = UserType.objects.get(id=2)
        # utype3 = UserType.objects.get(id=5)
        
        # purchase = Purchase.objects.filter(date__range=(first_day, last_day)).filter(Q(user__user_type=utype1) | Q(user__user_type=utype2) | Q(user__user_type=utype3)).order_by('-date', '-id')

        # for p in purchase:

        #     product = Product.objects.get(id=1)
        #     amount = float(product.price + p.user.user_type.price_variation) * float(p.quantity)

        #     p.amount = amount
        #     p.save()
