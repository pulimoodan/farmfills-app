from django.core.management.base import BaseCommand
from users.models import Purchase, User, Payment, Refund, Extra

class Command(BaseCommand):
    help = 'Creates daily transacion for all customers'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument('id', type=int)

    def handle(self, *args, **options):

        id = options['id']

        user = User.objects.get(id=id)

        transaction_data = []

        purchases = Purchase.objects.filter(user=user).order_by('-date', '-id')

        payments = Payment.objects.filter(user=user, paid=True).order_by('-date', '-id')

        refunds = Refund.objects.filter(user=user).order_by('-date', '-id')

        extras = Extra.objects.filter(user=user).order_by('-date', '-id')

        transaction_data = list(purchases) 

        transaction_data += list(payments)
        transaction_data += list(refunds)
        transaction_data += list(extras)

        transaction_data = sorted(transaction_data, key=lambda k: k.date, reverse=False)

        balance = 0
        transaction_id = 0

        for t in transaction_data:
            transaction_id += 1
            t.transaction_id = transaction_id
            if t.get_transaction_type() == 'payment' or t.get_transaction_type() == 'refund':
                t.balance = balance + t.amount
                balance += t.amount
            elif t.get_transaction_type() == 'purchase' or t.get_transaction_type() == 'extra':
                t.balance = balance - t.amount
                balance -= t.amount
            t.save()
        
        user.balance = balance
        user.last_transaction = transaction_id
        user.save()
