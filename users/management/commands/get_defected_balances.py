from django.core.management.base import BaseCommand
from users.views import get_last_transaction
from users.models import User

class Command(BaseCommand):
    help = 'Some payments found to be duplicated multiple times, this function returns customer ids with balance > 1000'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle(self, *args, **options):

        customers = User.objects.all().order_by('id')

        for c in customers:

            transaction = get_last_transaction(c)

            if transaction is not None and transaction.balance > 1000:
                self.stdout.write(self.style.SUCCESS('Updated : ' + str(c.id)))
