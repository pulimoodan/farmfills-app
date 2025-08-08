import pytz
from datetime import datetime
from users.models import  Purchase, Product
from django.core.management.base import BaseCommand

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
