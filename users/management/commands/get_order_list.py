from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from users.views import getEndBalanceOfMonth, last_day_of_month, getQuantityOfDate
from delivery.views import getDeliveryListByDate
from dispatch.views import getBulkCusomersOrder
from datetime import datetime, timedelta
from users.models import Staff, Purchase, Product, ExtraLess, Vacation, Subscription, UserType, User, Payment, Refund, Extra
import pytz

class Command(BaseCommand):
    help = 'Creates daily transacion for all customers'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument('date', type=str)

    def handle(self, *args, **options):

        data = []
        
        try:
            date = datetime.strptime(options['date'], '%Y-%m-%d').replace(tzinfo=pytz.UTC).date()

            data.append(['Date: ', date.strftime('%d %b, %Y')])
            data.append(['------------', '------------'])

            total = 0

            delivery_boys = Staff.objects.filter(delivery=True)

            for db in delivery_boys:

                delivery = getDeliveryListByDate(db.route, options['date'])

                data.append([db.name + ' (' + db.route.name + ')', str(delivery['total'])])

                total += delivery['total']

            bulk_customers_order = getBulkCusomersOrder(date)

            total += bulk_customers_order['total']

            for b in bulk_customers_order['list']:
                data.append([b['user'].delivery_name, str(b['total'])])
            
            data.append(['------------', '------------'])
            data.append(['Total', str(total)])

            for line in data:
                print(f"{line[0] : <50}{line[1] : ^50}")
        except Exception as e:
            print('==============     Error    ============')
            print(e)

        
