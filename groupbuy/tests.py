import json
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import GroupBuy, GroupBuyItem, Order


# High-level tests covering the core group buy flows (join, add item, status, filtering).
class CoreFlowTests(TestCase):
    def setUp(self):
        self.organizer = User.objects.create_user(username="organizer", password="pass12345")
        self.participant = User.objects.create_user(username="participant", password="pass12345")
        self.groupbuy = GroupBuy.objects.create(
            title="Test GroupBuy",
            store_name="Tesco Express",
            category=GroupBuy.CATEGORY_GROCERY,
            deadline=timezone.now() + timedelta(days=30),
            pickup_instructions="Meet at the main gate",
            description="Optional description",
            price=Decimal("2.50"),
            target_quantity=10,
            created_by=self.organizer,
        )

    def test_join_groupbuy_is_idempotent_for_same_user(self):
        self.client.login(username="participant", password="pass12345")
        join_url = reverse("join_groupbuy", kwargs={"groupbuy_id": self.groupbuy.id})

        response = self.client.post(join_url, data={"quantity": "1"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.filter(user=self.participant, groupbuy=self.groupbuy).count(), 1)
        self.assertEqual(Order.objects.get(user=self.participant, groupbuy=self.groupbuy).quantity, 1)

        response = self.client.post(join_url, data={"quantity": "3"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.filter(user=self.participant, groupbuy=self.groupbuy).count(), 1)
        self.assertEqual(Order.objects.get(user=self.participant, groupbuy=self.groupbuy).quantity, 3)

    def test_join_groupbuy_only_allowed_when_open(self):
        self.groupbuy.status = GroupBuy.STATUS_ORDERED
        self.groupbuy.save(update_fields=["status"])

        self.client.login(username="participant", password="pass12345")
        join_url = reverse("join_groupbuy", kwargs={"groupbuy_id": self.groupbuy.id})
        response = self.client.post(join_url, data={"quantity": "1"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.filter(user=self.participant, groupbuy=self.groupbuy).count(), 0)

    def test_add_item_ajax_creates_item(self):
        self.client.login(username="participant", password="pass12345")
        add_item_url = reverse("add_groupbuy_item", kwargs={"groupbuy_id": self.groupbuy.id})

        payload = {"item_name": "Sandwich", "quantity": "2", "price": "3.40"}
        response = self.client.post(
            add_item_url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(GroupBuyItem.objects.filter(groupbuy=self.groupbuy, added_by=self.participant).count(), 1)
        item = GroupBuyItem.objects.get(groupbuy=self.groupbuy, added_by=self.participant)
        self.assertEqual(item.item_name, "Sandwich")
        self.assertEqual(item.quantity, 2)

    def test_add_item_only_allowed_when_open(self):
        self.groupbuy.status = GroupBuy.STATUS_CLOSED
        self.groupbuy.save(update_fields=["status"])

        self.client.login(username="participant", password="pass12345")
        add_item_url = reverse("add_groupbuy_item", kwargs={"groupbuy_id": self.groupbuy.id})

        payload = {"item_name": "Tea", "quantity": "1", "price": "1.00"}
        response = self.client.post(
            add_item_url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(GroupBuyItem.objects.filter(groupbuy=self.groupbuy).count(), 0)

    def test_delete_item_only_allows_owner_or_organizer(self):
        item = GroupBuyItem.objects.create(
            groupbuy=self.groupbuy,
            added_by=self.participant,
            item_name="Tea",
            quantity=1,
            price=Decimal("1.00"),
        )
        delete_url = reverse("delete_groupbuy_item", kwargs={"groupbuy_id": self.groupbuy.id, "item_id": item.id})

        self.client.login(username="organizer", password="pass12345")
        response = self.client.post(delete_url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(GroupBuyItem.objects.filter(id=item.id).exists())

        item = GroupBuyItem.objects.create(
            groupbuy=self.groupbuy,
            added_by=self.participant,
            item_name="Coffee",
            quantity=1,
            price=Decimal("2.00"),
        )
        delete_url = reverse("delete_groupbuy_item", kwargs={"groupbuy_id": self.groupbuy.id, "item_id": item.id})

        other_user = User.objects.create_user(username="other", password="pass12345")
        self.client.logout()
        self.client.login(username="other", password="pass12345")
        response = self.client.post(delete_url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 404)
        self.assertTrue(GroupBuyItem.objects.filter(id=item.id).exists())

    def test_delete_item_disallowed_when_closed_for_non_organizer(self):
        self.groupbuy.status = GroupBuy.STATUS_CLOSED
        self.groupbuy.save(update_fields=["status"])

        item = GroupBuyItem.objects.create(
            groupbuy=self.groupbuy,
            added_by=self.participant,
            item_name="Snack",
            quantity=1,
            price=Decimal("1.50"),
        )
        delete_url = reverse("delete_groupbuy_item", kwargs={"groupbuy_id": self.groupbuy.id, "item_id": item.id})

        self.client.login(username="participant", password="pass12345")
        response = self.client.post(delete_url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 400)
        self.assertTrue(GroupBuyItem.objects.filter(id=item.id).exists())

    def test_update_status_only_organizer_can_update(self):
        update_status_url = reverse("update_groupbuy_status", kwargs={"groupbuy_id": self.groupbuy.id})

        self.client.login(username="participant", password="pass12345")
        response = self.client.post(
            update_status_url,
            data={"status": GroupBuy.STATUS_ORDERED},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 403)

        self.client.logout()
        self.client.login(username="organizer", password="pass12345")
        response = self.client.post(
            update_status_url,
            data={"status": GroupBuy.STATUS_ORDERED},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        self.groupbuy.refresh_from_db()
        self.assertEqual(self.groupbuy.status, GroupBuy.STATUS_ORDERED)

    def test_my_orders_category_filter(self):
        food_groupbuy = GroupBuy.objects.create(
            title="Food GB",
            store_name="Cafe",
            category=GroupBuy.CATEGORY_FOOD,
            deadline=timezone.now() + timedelta(days=30),
            pickup_instructions="Pick up",
            price=Decimal("1.00"),
            target_quantity=5,
            created_by=self.organizer,
        )

        Order.objects.update_or_create(user=self.participant, groupbuy=self.groupbuy, defaults={"quantity": 1})
        Order.objects.update_or_create(user=self.participant, groupbuy=food_groupbuy, defaults={"quantity": 1})

        self.client.login(username="participant", password="pass12345")
        response = self.client.get(reverse("my_orders") + "?category=" + GroupBuy.CATEGORY_GROCERY)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.groupbuy.title)
        self.assertNotContains(response, food_groupbuy.title)

    def test_delete_order_only_allows_owner(self):
        order = Order.objects.create(user=self.participant, groupbuy=self.groupbuy, quantity=1)
        delete_url = reverse("delete_order", kwargs={"order_id": order.id})

        self.client.login(username="organizer", password="pass12345")
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Order.objects.filter(id=order.id).exists())

        self.client.logout()
        self.client.login(username="participant", password="pass12345")
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Order.objects.filter(id=order.id).exists())
