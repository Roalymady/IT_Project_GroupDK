from django.db import models
from django.contrib.auth.models import User


class GroupBuy(models.Model):

    CATEGORY_FOOD = "Food"
    CATEGORY_GROCERY = "Grocery"
    CATEGORY_STATIONERY = "Stationery"
    CATEGORY_OTHER = "Other"

    CATEGORY_CHOICES = [
        (CATEGORY_FOOD, "Food"),
        (CATEGORY_GROCERY, "Grocery"),
        (CATEGORY_STATIONERY, "Stationery"),
        (CATEGORY_OTHER, "Other"),
    ]

    STATUS_OPEN = "open"
    STATUS_ORDERED = "ordered"
    STATUS_CLOSED = "closed"

    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_ORDERED, "Ordered"),
        (STATUS_CLOSED, "Closed"),
    ]

    title = models.CharField(max_length=200)

    store_name = models.CharField(max_length=200, blank=True, null=True)

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, blank=True, null=True)

    deadline = models.DateTimeField(blank=True, null=True)

    pickup_instructions = models.TextField(blank=True, null=True)

    description = models.TextField(blank=True, null=True)

    price = models.DecimalField(max_digits=8, decimal_places=2)

    target_quantity = models.IntegerField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Order(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    groupbuy = models.ForeignKey(GroupBuy, on_delete=models.CASCADE)

    quantity = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "groupbuy"],
                name="uniq_order_user_groupbuy",
            ),
        ]


class GroupBuyItem(models.Model):
    groupbuy = models.ForeignKey(GroupBuy, on_delete=models.CASCADE, related_name="items")
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
