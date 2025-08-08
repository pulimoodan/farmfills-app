from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from users.views import checkDeliveyInDateFromSub
from users.models import Subscription

class Command(BaseCommand):
    help = '-'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def handle(self, *args, **options):
        today = timezone.localtime(timezone.now()).date()
        subs = Subscription.objects.filter(sub_type='alternate').filter(Q(end_date=None) | Q(end_date__gte=today))
        for s in subs:
            s.end_date = today
            s.save()
            if checkDeliveyInDateFromSub(s, today + timedelta(days=1)):
                new_sub = Subscription(user=s.user, sub_type="alternate", start_date=today + timedelta(days=2), alternate_quantity=s.alternate_quantity)
                new_sub.save()
            else:
                new_sub = Subscription(user=s.user, sub_type="alternate", start_date=today + timedelta(days=1), alternate_quantity=s.alternate_quantity)
                new_sub.save()
        self.stdout.write(self.style.SUCCESS('Successfully updated alternate subscriptions'))
