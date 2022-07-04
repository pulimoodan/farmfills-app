from django.core.management.base import BaseCommand, CommandError
from delivery.views import getDeliveryListByDate
import pytz
from django.utils import timezone
from datetime import datetime, timedelta
from users.views import getEndBalanceOfMonth, last_day_of_month
from users.models import Staff, Purchase, Product, ExtraLess, Vacation, Subscription, UserType, User

class Command(BaseCommand):
    help = 'Creates transacions of a specific date for all customers'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument('date', type=str)

    def handle(self, *args, **options):
        
        product = Product.objects.get(id=1)

        date = datetime.strptime(options['date'], '%Y-%m-%d').replace(tzinfo=pytz.UTC)

        delivery_boys = Staff.objects.filter(delivery=True)

        for db in delivery_boys:

            deliveryData = getDeliveryListByDate(db.route, options['date'])

            for d in deliveryData['list']:
                if d['packet'] != 0:
                    amount = float(product.price + d['user'].user_type.price_variation) * float(d['packet']/2)
                    last_day = last_day_of_month(date)
                    balance = float(getEndBalanceOfMonth(last_day, d['user']) )- amount
                    purchase = Purchase(date=date, quantity=d['packet']/2, amount=amount, balance=balance, product=product, user=d['user'], delivered_by=db)
                    purchase.save()
            
            for d in deliveryData['assigned']:
                if d['packet'] != 0:
                    amount = float(product.price + d['user'].user_type.price_variation) * float(d['packet']/2)
                    last_day = last_day_of_month(date)
                    balance = float(getEndBalanceOfMonth(last_day, d['user']) )- amount
                    purchase = Purchase(date=date, quantity=d['packet']/2, amount=amount, balance=balance, product=product, user=d['user'], delivered_by=db)
                    purchase.save()
        
        bulkType = UserType.objects.get(id=8)
        bulkCustomers = User.objects.filter(user_type = bulkType)

        for b in bulkCustomers:

            extraless = ExtraLess.objects.filter(user=b)
            vacations = Vacation.objects.filter(user=b)
            subs = Subscription.objects.filter(user=b)

            in_vacation = False

            thisdate = date

            for e in extraless:
                if e.start_date <= thisdate.date() and e.end_date >= thisdate.date() :
                    amount = float(product.price + b.user_type.price_variation) * float(e.quantity)
                    last_day = last_day_of_month(thisdate)
                    balance = float(getEndBalanceOfMonth(last_day, b) )- amount
                    purchase = Purchase(date=thisdate, quantity=e.quantity, amount=amount, balance=balance, product=product, user=b)
                    purchase.save()
                    in_vacation = True
                    break
            
            if not in_vacation:
                for v in vacations:

                    if v.start_date <= thisdate.date() and v.end_date is None :
                        in_vacation = True
                        break
                    elif v.end_date is not None:
                        if v.start_date <= thisdate.date() and v.end_date >= thisdate.date():
                            in_vacation = True
                            break
            
            if not in_vacation:
                for s in subs:

                    if s.start_date <= thisdate.date() and s.end_date is None :
                        quantity =  0
                        try:
                            quantity = int(getQuantityOfDate(s, date.date()))
                        except:
                            pass
                        if quantity != 0:
                            amount = float(product.price + b.user_type.price_variation) * quantity
                            last_day = last_day_of_month(thisdate)
                            balance = float(getEndBalanceOfMonth(last_day, b) )- amount
                            purchase = Purchase(date=thisdate, quantity=quantity, amount=amount, balance=balance, product=product, user=b)
                            purchase.save()
                    elif s.end_date is not None:
                        if s.start_date <= thisdate.date() and s.end_date >= thisdate.date():
                            quantity =  0
                            try:
                                quantity = int(getQuantityOfDate(s, date()))
                            except:
                                pass
                            if quantity != 0:
                                amount = float(product.price + b.user_type.price_variation) * quantity
                                last_day = last_day_of_month(thisdate)
                                balance = float(getEndBalanceOfMonth(last_day, b) )- amount
                                purchase = Purchase(date=thisdate, quantity=quantity, amount=amount, balance=balance, product=product, user=b)
                                purchase.save()
        
            self.stdout.write(self.style.SUCCESS('Successfully created daily transactions'))
