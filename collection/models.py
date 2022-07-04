from django.db import models
from users.models import User, Staff, Payment
from django.utils import timezone

# collection model
class Collection(models.Model):

    id = models.AutoField(primary_key=True)

    date = models.DateTimeField(auto_now_add=True)

    amount = models.DecimalField(max_digits=20, decimal_places=2)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="payment user",
    )

    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        verbose_name="payment data",
    )


# handover model
class HandOver(models.Model):

    id = models.AutoField(primary_key=True)

    date = models.DateTimeField(auto_now_add=True)

    amount = models.DecimalField(max_digits=20, decimal_places=2)

    to = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        verbose_name="staff",
    )


# expenses model
class Expenses(models.Model):

    id = models.AutoField(primary_key=True)

    date = models.DateTimeField(auto_now_add=True)

    amount = models.DecimalField(max_digits=20, decimal_places=2)

    note = models.TextField()