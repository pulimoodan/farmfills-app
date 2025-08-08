from django.core.management.base import BaseCommand
import subprocess
from users.models import User

class Command(BaseCommand):
    help = 'Update every customers balance'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle(self, *args, **options):

        customers = User.objects.all().order_by('id')

        for c in customers:

            subprocess.Popen(["python3", "manage.py", "update_transactions_balance", str(c.id) ], stdout=subprocess.PIPE).communicate()
        
            self.stdout.write(self.style.SUCCESS('Updated : ' + str(c.id)))
