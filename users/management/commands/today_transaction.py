from django.core.management.base import BaseCommand, CommandError
from delivery.views import getDeliveryList
import pytz
import subprocess
from django.utils import timezone
from datetime import datetime, timedelta
from users.views import getEndBalanceOfMonth, last_day_of_month
from delivery.models import DeliveryData
from users.models import Staff, Purchase, Product, ExtraLess, Vacation, Subscription, UserType, User, Product
from django.core import management

class Command(BaseCommand):
    help = 'Creates daily transacion for all customers'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle(self, *args, **options):

        product = Product.objects.get(id=1)
        data = DeliveryData.objects.filter(date=timezone.localtime(timezone.now()).date())

        for d in data:
            amount = float(product.price + d.user.user_type.price_variation) * float(d.packet/2)
            if d.packet > 0:
                if d.bulk:
                    purchase = Purchase(date=timezone.localtime(timezone.now()), quantity=d.packet/2, amount=amount, balance=0, product=product, user=d.user)
                    purchase.save()
                    management.call_command('update_transactions_balance', str(d.user.id), verbosity=0)
                else:
                    dboy = Staff.objects.get(delivery=True, route=d.route)
                    purchase = Purchase(date=timezone.localtime(timezone.now()), quantity=d.packet/2, amount=amount, balance=0, product=product, user=d.user, delivered_by=dboy)
                    purchase.save()
                    management.call_command('update_transactions_balance', str(d.user.id), verbosity=0)
        
        print(timezone.localtime(timezone.now()).strftime('%d %b, %Y') + ': Successfully created daily transactions')