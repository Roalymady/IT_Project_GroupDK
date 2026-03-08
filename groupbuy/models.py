from django.db import models
from django.contrib.auth.models import User


class GroupBuy(models.Model):

    title = models.CharField(max_length=200)

    description = models.TextField()

    price = models.DecimalField(max_digits=8, decimal_places=2)

    target_quantity = models.IntegerField()

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Order(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    groupbuy = models.ForeignKey(GroupBuy, on_delete=models.CASCADE)

    quantity = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)