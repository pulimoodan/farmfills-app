from django.db import models
from users.models import User, Product, Staff


PAYMENT_MODES =(
    ("online", "Online"),
    ("cash", "Cash"),
    ("bank transfer", "Bank Transfer")
)


# payments model
class DPayment(models.Model):

    id = models.AutoField(primary_key=True)

    date = models.DateTimeField()

    amount = models.DecimalField(max_digits=20, decimal_places=2)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="payment user",
    )

    mode = models.CharField(max_length=50, blank=True, null=True, choices = PAYMENT_MODES)

    order_id = models.CharField(max_length=50, blank=True, null=True)

    payment_id = models.CharField(max_length=50, blank=True, null=True)

    description = models.TextField(blank=True, null=True)

    paid = models.BooleanField()

    balance = models.DecimalField(max_digits=20, decimal_places=2)

    def get_transaction_type(self):
        transaction_type = 'payment'
        return transaction_type


# purchase model
class DPurchase(models.Model):

    id = models.AutoField(primary_key=True)

    date = models.DateTimeField()

    amount = models.DecimalField(max_digits=20, decimal_places=2)

    quantity = models.DecimalField(max_digits=20, decimal_places=2)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="purchase user",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="purchase product",
    )

    delivered_by = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        verbose_name="delivery boy",
        blank=True, 
        null=True
    )

    balance = models.DecimalField(max_digits=20, decimal_places=2)

    def get_transaction_type(self):
        transaction_type = 'purchase'
        return transaction_type


REFUND_REASONS =(
    ("not delivered", "Not delivered"),
    ("leaked", "Leaked"),
    ("spoiled", "Spoiled")
)


# refund model
class DRefund(models.Model):

    id = models.AutoField(primary_key=True)

    date = models.DateTimeField()

    amount = models.DecimalField(max_digits=20, decimal_places=2)

    quantity = models.DecimalField(max_digits=20, decimal_places=2)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="refund user",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="extra product",
    )

    reason = models.CharField(max_length=50, blank=True, null=True, choices = REFUND_REASONS)

    balance = models.DecimalField(max_digits=20, decimal_places=2)

    def get_transaction_type(self):
        transaction_type = 'refund'
        return transaction_type


# extra
class DExtra(models.Model):

    id = models.AutoField(primary_key=True)

    date = models.DateTimeField()

    amount = models.DecimalField(max_digits=20, decimal_places=2)

    quantity = models.DecimalField(max_digits=20, decimal_places=2)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="extra user",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="extra product",
    )

    note = models.TextField(blank=True, null=True)

    balance = models.DecimalField(max_digits=20, decimal_places=2)

    def get_transaction_type(self):
        transaction_type = 'extra'
        return transaction_type