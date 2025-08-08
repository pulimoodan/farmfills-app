from users.models import User
from users.views import get_last_transaction
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Creates daily transacion for all customers'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument('id', type=int)

    def handle(self, *args, **options):

        id = options['id']

        user = User.objects.get(id=id)

        last_transaction = get_last_transaction(user)

        print(last_transaction.balance)
