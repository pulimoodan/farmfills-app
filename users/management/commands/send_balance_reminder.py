from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from users.views import getEndBalanceOfMonth, getNextDelivery, getNextDeliveryAfterTomorrow
from datetime import datetime, timedelta
from users.models import ExtraLess, Vacation, Subscription, UserType, User, Product
import pytz
import http.client
from django.conf import settings

class Command(BaseCommand):
    help = 'Creates daily transacion for all customers'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle(self, *args, **options):
        customers = User.objects.filter(user_type__payment_type='prepaid', user_type__suspend=True)
        for c in customers:
            last_date = timezone.localtime(timezone.now())
            balance = getEndBalanceOfMonth(last_date, c)
            subs = Subscription.objects.filter(user=c)
            vacations = Vacation.objects.filter(user=c)
            extras = ExtraLess.objects.filter(user=c)
            milk = Product.objects.get(id=1)
            next_delivery = getNextDelivery(subs, vacations, extras)
            tomorrow = (last_date + timedelta(days=1)).strftime("%b %d, %Y")
            if next_delivery is not None:
                if tomorrow == next_delivery['date']:
                    price_for_next_delivery = (milk.price + c.user_type.price_variation) * next_delivery['quantity']
                    
                    # check balance for next delivery
                    if balance < price_for_next_delivery:
                        conn = http.client.HTTPSConnection("api.msg91.com")
                        url = "/api/v5/flow?flow_id=" + settings.ENV('MSG91_FLOW_ID') + "&mobile=91" + c.mobile + "&authkey=" + settings.ENV('MSG91_AUTH_KEY')
                        url = url.replace(" ","")
                        conn.request("POST", url)
                        res = conn.getresponse()
                        data = res.read()
                        print(data.decode("utf-8"))
                        continue
                    
                    # check balance for next 2 delivery
                    balance -= price_for_next_delivery
                    next_delivery = getNextDeliveryAfterTomorrow(subs, vacations, extras)
                    price_for_next_delivery = (milk.price + c.user_type.price_variation) * next_delivery['quantity']
                    if balance < price_for_next_delivery:
                        conn = http.client.HTTPSConnection("api.msg91.com")
                        url = "/api/v5/flow?flow_id=" + settings.ENV('MSG91_FLOW_ID') + "&mobile=91" + c.mobile + "&authkey=" + settings.ENV('MSG91_AUTH_KEY')
                        url = url.replace(" ","")
                        conn.request("POST", url)
                        res = conn.getresponse()
                        data = res.read()
                        print(data.decode("utf-8"))
                
                    


        
