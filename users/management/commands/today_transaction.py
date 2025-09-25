from datetime import datetime, time, timezone as dt_timezone
from django.core import management
from users.models import Staff, Purchase
from django.core.management.base import BaseCommand
from farmfills_admin.business import daily_delivery_query

class Command(BaseCommand):
    help = 'Creates daily transacion for all customers'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument('date', type=str, nargs='?', default=datetime.today().strftime('%Y-%m-%d'))

    def handle(self, *args, **options):
        result = daily_delivery_query(options['date'])
        selected_date = datetime.strptime(options['date'], "%Y-%m-%d")
        purchase_datetime = datetime.combine(selected_date, time.min).replace(tzinfo=dt_timezone.utc)

        for row in result:
            (user_id, delivery_name, user_type_id, _, _, route_id, _, assigned, packets, cost) = row
            amount = cost * (packets / 2)
            
            if Purchase.objects.filter(user_id=user_id, date__date=selected_date).exists():
                continue

            if user_type_id == 8:
                purchase = Purchase(date=purchase_datetime, quantity=packets/2, amount=amount, balance=0, product_id=1, user_id=user_id)
                purchase.save()
            else:
                dboy = Staff.objects.get(delivery=True, route_id=route_id)
                purchase = Purchase(date=purchase_datetime, quantity=packets/2, amount=amount, balance=0, product_id=1, user_id=user_id, delivered_by=dboy)
                purchase.save()
            management.call_command('update_transactions_balance', str(user_id), verbosity=0)
        
        print(selected_date.strftime('%d %b, %Y') + ': Successfully created daily transactions')
