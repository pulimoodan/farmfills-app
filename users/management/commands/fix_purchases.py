from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta, date, time
from collections import defaultdict

from users.models import User, Purchase, Payment, Refund


class Command(BaseCommand):
    help = "Reconcile balances and create missing purchases for a specific customer."

    START_DATE = date(2021, 3, 1)
    END_DATE = date(2024, 4, 30)

    def add_arguments(self, parser):
        parser.add_argument(
            "customer_id",
            type=int,
            help="ID of the customer to check"
        )

    def handle(self, *args, **options):
        customer_id = options["customer_id"]
        try:
            customer = User.objects.get(id=customer_id)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Customer with id {customer_id} not found."))
            return

        self.stdout.write(f"Checking {customer.name} (ID: {customer.id})...")

        start_dt = timezone.make_aware(datetime.combine(self.START_DATE, time.min))
        end_dt = timezone.make_aware(datetime.combine(self.END_DATE, time.max))

        self.reconcile_customer(customer, start_dt, end_dt)

    def reconcile_customer(self, customer, start_dt, end_dt):
        # Fetch all transactions within range
        purchases = list(Purchase.objects.filter(user=customer, date__range=(start_dt, end_dt)))
        payments = list(Payment.objects.filter(user=customer, date__range=(start_dt, end_dt), paid=True))
        refunds = list(Refund.objects.filter(user=customer, date__range=(start_dt, end_dt)))


        txns = []
        for p in purchases:
            txns.append({"type": "purchase", "amount": float(p.amount), "date": p.date})
        for p in payments:
            txns.append({"type": "payment", "amount": float(p.amount), "date": p.date})
        for r in refunds:
            txns.append({"type": "refund", "amount": float(r.amount), "date": r.date})

        if not txns:
            self.stdout.write("No transactions found in the period.")
            return

        # Sort by date
        txns.sort(key=lambda x: x["date"])

        # Group transactions by month
        months = defaultdict(list)
        for t in txns:
            month_key = timezone.localtime(t["date"]).strftime("%Y-%m")
            months[month_key].append(t)

        # Iterate month by month across the full calendar period
        current_month = self.START_DATE.replace(day=1)
        end_month = self.END_DATE.replace(day=1)

        previous_txns = []
        for model in [Purchase, Refund]:
            qs = model.objects.filter(user=customer, date__lt=start_dt).order_by("-date").first()
            if qs:
                previous_txns.append(qs)
        qs = Payment.objects.filter(user=customer, date__lt=start_dt, paid=True).order_by("-date").first()
        if qs:
            previous_txns.append(qs)

        last_before = max(previous_txns, key=lambda t: t.date, default=None)
        running_balance = float(last_before.balance) if last_before else 0

        print("Starting balance", running_balance)

        while current_month <= end_month:
            key = current_month.strftime("%Y-%m")
            month_txns = months.get(key, [])

            # Update running balance for this month
            for t in month_txns:
                if t["type"] == "purchase":
                    running_balance -= t["amount"]
                else:  # payment or refund
                    running_balance += t["amount"]

            # Determine next calendar month
            next_month = (current_month.replace(day=28) + timedelta(days=4)).replace(day=1)
            next_key = next_month.strftime("%Y-%m")
            next_txns = months.get(next_key, [])
            next_payments = [t for t in next_txns if t["type"] in ["payment"]]
            print(key, running_balance, len(next_payments))

            total_next_payments = sum(p["amount"] for p in next_payments)
            diff = running_balance + total_next_payments
            print("Next month payment", next_payments)

            if diff > 0:
                missing_date = self.get_last_day_of_month(key)
                with transaction.atomic():
                    Purchase.objects.create(
                        user=customer,
                        quantity=abs(diff) / 60,
                        amount=abs(diff),
                        date=missing_date,
                        product_id=1,
                        balance=0
                    )
                running_balance -= diff
                self.stdout.write(
                    f"✅ Added missing purchase {abs(diff)} on {missing_date} for {customer.name} ({key})\n\n"
                )

            # Move to next calendar month
            current_month = next_month

    def get_last_day_of_month(self, year_month):
        year, month = map(int, year_month.split("-"))
        if month == 12:
            dt = datetime(year, 12, 31)
        else:
            next_month = datetime(year, month + 1, 1)
            dt = next_month - timedelta(days=1)
        return timezone.make_aware(datetime.combine(dt, time.min))

