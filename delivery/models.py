from django.db import models
from users.models import User, Route, Area

# delivery data
class DeliveryData(models.Model):
    id = models.AutoField(primary_key=True)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="assigned user",
    )

    packet = models.IntegerField()

    order = models.IntegerField()

    is_extra = models.BooleanField(default=False)

    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        verbose_name="delivery route",
        null=True,
    )

    area = models.ForeignKey(
        Area,
        on_delete=models.CASCADE,
        verbose_name="delivery area",
        null=True,
    )

    bulk = models.BooleanField(default=False)

    date = models.DateField(auto_now_add=True)