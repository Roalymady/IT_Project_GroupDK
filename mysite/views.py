# Django views for authentication and the core group-buy flows (dashboard, CRUD, items, orders).
import json
from datetime import timedelta
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from groupbuy.models import GroupBuy, GroupBuyItem, Order

@login_required
def dashboard(request):
    # Render the dashboard and ensure demo group buys exist with varied categories/status/deadlines.
    now = timezone.now()

    sample_organizers = [
        "Ash",
        "Emily",
        "Noah",
    ]

    organizer_users = []
    for username in sample_organizers:
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_unusable_password()
            user.save(update_fields=["password"])
        organizer_users.append(user)

    sample_groupbuys = [
        {
            "title": "Food: Bubble Tea Happy Hour",
            "store_name": "Byres Road Tea House",
            "category": GroupBuy.CATEGORY_FOOD,
            "description": "From Byres Road Tea House. Meet at the University of Glasgow library entrance at 6:30 PM.",
            "pickup_instructions": "Meet at the University of Glasgow library entrance at 6:30 PM.",
            "deadline": now + timedelta(days=2, hours=3),
            "price": Decimal("5.50"),
            "target_quantity": 10,
            "status": GroupBuy.STATUS_OPEN,
            "created_by": organizer_users[0],
        },
        {
            "title": "Grocery: Tesco Meal Deal",
            "store_name": "Tesco Express (Byres Road)",
            "category": GroupBuy.CATEGORY_GROCERY,
            "description": "Pick up near Gilmorehill Campus. We will split the discount once we reach the target.",
            "pickup_instructions": "Pick up near Gilmorehill Campus.",
            "deadline": now + timedelta(days=1, hours=6),
            "price": Decimal("3.40"),
            "target_quantity": 12,
            "status": GroupBuy.STATUS_ORDERED,
            "created_by": organizer_users[1],
        },
        {
            "title": "Stationery: WHSmith Notebooks",
            "store_name": "WHSmith (Buchanan Street)",
            "category": GroupBuy.CATEGORY_STATIONERY,
            "description": "Collect at Buchanan Street. Perfect for exam revision notes and group study sessions.",
            "pickup_instructions": "Collect at Buchanan Street.",
            "deadline": now - timedelta(hours=4),
            "price": Decimal("2.99"),
            "target_quantity": 20,
            "status": GroupBuy.STATUS_CLOSED,
            "created_by": organizer_users[2],
        },
    ]

    for sample in sample_groupbuys:
        groupbuy, _created = GroupBuy.objects.get_or_create(
            title=sample["title"],
            defaults={
                "description": sample["description"],
                "store_name": sample["store_name"],
                "category": sample["category"],
                "pickup_instructions": sample["pickup_instructions"],
                "deadline": sample["deadline"],
                "price": sample["price"],
                "target_quantity": sample["target_quantity"],
                "status": sample["status"],
                "created_by": sample["created_by"],
            },
        )

        if groupbuy.created_by_id == request.user.id:
            groupbuy.created_by = sample["created_by"]
            groupbuy.save(update_fields=["created_by"])

        updated_fields = []
        if groupbuy.store_name != sample["store_name"]:
            groupbuy.store_name = sample["store_name"]
            updated_fields.append("store_name")
        if groupbuy.category != sample["category"]:
            groupbuy.category = sample["category"]
            updated_fields.append("category")
        if groupbuy.pickup_instructions != sample["pickup_instructions"]:
            groupbuy.pickup_instructions = sample["pickup_instructions"]
            updated_fields.append("pickup_instructions")
        if groupbuy.description != sample["description"]:
            groupbuy.description = sample["description"]
            updated_fields.append("description")
        if groupbuy.deadline != sample["deadline"]:
            groupbuy.deadline = sample["deadline"]
            updated_fields.append("deadline")
        if groupbuy.status != sample["status"]:
            groupbuy.status = sample["status"]
            updated_fields.append("status")
        if updated_fields:
            groupbuy.save(update_fields=updated_fields)

    groupbuys = GroupBuy.objects.all().order_by("-created_at")
    for groupbuy in groupbuys:
        groupbuy.display_category = groupbuy.category or "Other"
        if not groupbuy.deadline:
            groupbuy.deadline = now + timedelta(days=3)
            groupbuy.save(update_fields=["deadline"])

    return render(request, "dashboard.html", {
        "groupbuys": groupbuys
    })


@login_required
def create_groupbuy(request):
    # Create a new group buy (organizer flow) with server-side validation and form repopulation on errors.

    form_data = {
        "title": "",
        "store_name": "",
        "category": "",
        "deadline": "",
        "pickup_instructions": "",
        "description": "",
        "price": "",
        "target_quantity": "",
    }

    if request.method == "POST":

        title = (request.POST.get("title") or "").strip()
        store_name = (request.POST.get("store_name") or "").strip()
        category = (request.POST.get("category") or "").strip()
        deadline = (request.POST.get("deadline") or "").strip()
        pickup_instructions = (request.POST.get("pickup_instructions") or "").strip()
        description = (request.POST.get("description") or "").strip()
        raw_price = (request.POST.get("price") or "").strip()
        raw_target_quantity = (request.POST.get("target_quantity") or "").strip()

        form_data = {
            "title": title,
            "store_name": store_name,
            "category": category,
            "deadline": deadline,
            "pickup_instructions": pickup_instructions,
            "description": description,
            "price": raw_price,
            "target_quantity": raw_target_quantity,
        }

        try:
            price = Decimal(raw_price)
        except (InvalidOperation, TypeError):
            price = None

        try:
            target_quantity = int(raw_target_quantity)
        except (ValueError, TypeError):
            target_quantity = None

        if not title or not store_name or not category or not deadline or not pickup_instructions:
            messages.error(request, "Please fill in all required fields.")
            return render(request, "create_groupbuy.html", {"form_data": form_data})

        if category not in dict(GroupBuy.CATEGORY_CHOICES):
            messages.error(request, "Please choose a valid category.")
            return render(request, "create_groupbuy.html", {"form_data": form_data})

        if price is None or price <= 0:
            messages.error(request, "Please enter a valid price.")
            return render(request, "create_groupbuy.html", {"form_data": form_data})

        if target_quantity is None or target_quantity <= 0:
            messages.error(request, "Please enter a valid target quantity.")
            return render(request, "create_groupbuy.html", {"form_data": form_data})

        from django.utils.dateparse import parse_datetime
        from django.utils import timezone

        deadline_input = deadline.strip()
        if len(deadline_input) == 16:
            deadline_input = deadline_input + ":00"
        deadline_dt = parse_datetime(deadline_input)
        if deadline_dt is not None and timezone.is_naive(deadline_dt):
            deadline_dt = timezone.make_aware(deadline_dt, timezone.get_current_timezone())

        if deadline_dt is None:
            messages.error(request, "Please choose a valid deadline.")
            return render(request, "create_groupbuy.html", {"form_data": form_data})

        GroupBuy.objects.create(
            title=title,
            description=description,
            store_name=store_name,
            category=category,
            deadline=deadline_dt,
            pickup_instructions=pickup_instructions,
            price=price,
            target_quantity=target_quantity,
            created_by=request.user
        )
        return redirect("dashboard")

    return render(request, "create_groupbuy.html", {"form_data": form_data})

@login_required
@require_POST
def delete_groupbuy(request, groupbuy_id):
    # Delete a group buy (organizer-only).

    groupbuy = get_object_or_404(GroupBuy, id=groupbuy_id)

    if groupbuy.created_by == request.user:
        groupbuy.delete()

    return redirect("dashboard")

def login_view(request):
    # Log a user in and optionally persist the session when "remember" is selected.
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        remember = request.POST.get("remember")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:

            login(request, user)

            if remember:
                request.session.set_expiry(1209600)
            else:
                request.session.set_expiry(0)

            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")

def register_view(request):
    # Register a new user account (minimal username/password signup).

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username and password:
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(
                    username=username,
                    password=password
                )
                messages.success(request, "Registration successful. Please log in.")
                return redirect("login")
            else:
                messages.error(request, "Username already exists.")

    return render(request, "register.html")


@login_required
def groupbuy_detail(request, groupbuy_id):
    # Show a group buy with participant orders and added items.

    groupbuy = get_object_or_404(GroupBuy, id=groupbuy_id)

    orders = Order.objects.filter(groupbuy=groupbuy).select_related("user")
    items = GroupBuyItem.objects.filter(groupbuy=groupbuy).select_related("added_by").order_by("-created_at")

    return render(request, "detail.html", {
        "groupbuy": groupbuy,
        "orders": orders,
        "items": items,
    })

@login_required
@require_POST
def update_groupbuy_status(request, groupbuy_id):
    # Update a group buy status (organizer-only) and support both AJAX and standard form posts.
    groupbuy = get_object_or_404(GroupBuy, id=groupbuy_id)
    if groupbuy.created_by_id != request.user.id:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"detail": "Forbidden"}, status=403)
        messages.error(request, "You do not have permission to update this status.")
        return redirect("groupbuy_detail", groupbuy_id=groupbuy_id)

    status = (request.POST.get("status") or "").strip()
    allowed = dict(GroupBuy.STATUS_CHOICES)
    if status not in allowed:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"detail": "Invalid status"}, status=400)
        messages.error(request, "Please choose a valid status.")
        return redirect("groupbuy_detail", groupbuy_id=groupbuy_id)

    groupbuy.status = status
    groupbuy.save(update_fields=["status"])
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"status": groupbuy.status, "label": allowed[status]})
    messages.success(request, "Status updated.")
    return redirect("groupbuy_detail", groupbuy_id=groupbuy_id)

@login_required
@require_POST
def add_groupbuy_item(request, groupbuy_id):
    # Add a group buy item via AJAX (JSON) or fallback form submission.
    groupbuy = get_object_or_404(GroupBuy, id=groupbuy_id)

    if groupbuy.status != GroupBuy.STATUS_OPEN:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"detail": "This group buy is not open."}, status=400)
        messages.error(request, "This group buy is not open for adding items.")
        return redirect("groupbuy_detail", groupbuy_id=groupbuy_id)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        try:
            payload = json.loads(request.body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return JsonResponse({"detail": "Invalid JSON"}, status=400)
        item_name = (payload.get("item_name") or "").strip()
        raw_quantity = (payload.get("quantity") or "").strip()
        raw_price = (payload.get("price") or "").strip()
    else:
        item_name = (request.POST.get("item_name") or "").strip()
        raw_quantity = (request.POST.get("quantity") or "").strip()
        raw_price = (request.POST.get("price") or "").strip()

    try:
        quantity = int(raw_quantity)
    except (ValueError, TypeError):
        quantity = None

    try:
        price = Decimal(raw_price)
    except (InvalidOperation, TypeError):
        price = None

    if not item_name:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"detail": "Item name is required"}, status=400)
        messages.error(request, "Item name is required.")
        return redirect("groupbuy_detail", groupbuy_id=groupbuy_id)
    if quantity is None or quantity <= 0:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"detail": "Quantity must be a positive integer"}, status=400)
        messages.error(request, "Please enter a valid quantity.")
        return redirect("groupbuy_detail", groupbuy_id=groupbuy_id)
    if price is None or price <= 0:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"detail": "Price must be a positive number"}, status=400)
        messages.error(request, "Please enter a valid price.")
        return redirect("groupbuy_detail", groupbuy_id=groupbuy_id)

    item = GroupBuyItem.objects.create(
        groupbuy=groupbuy,
        added_by=request.user,
        item_name=item_name,
        quantity=quantity,
        price=price,
    )

    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        messages.success(request, "Item added.")
        return redirect("groupbuy_detail", groupbuy_id=groupbuy_id)

    return JsonResponse(
        {
            "id": item.id,
            "item_name": item.item_name,
            "quantity": item.quantity,
            "price": str(item.price),
            "added_by": request.user.username,
            "delete_url": reverse("delete_groupbuy_item", kwargs={"groupbuy_id": groupbuy.id, "item_id": item.id}),
        },
        status=201,
    )

@login_required
@require_POST
def delete_groupbuy_item(request, groupbuy_id, item_id):
    groupbuy = get_object_or_404(GroupBuy, id=groupbuy_id)
    item = get_object_or_404(GroupBuyItem, id=item_id, groupbuy=groupbuy)

    is_owner = item.added_by_id == request.user.id
    is_organizer = groupbuy.created_by_id == request.user.id
    if not (is_owner or is_organizer):
        return JsonResponse({"detail": "Not found"}, status=404) if request.headers.get("X-Requested-With") == "XMLHttpRequest" else redirect("groupbuy_detail", groupbuy_id=groupbuy_id)

    if groupbuy.status == GroupBuy.STATUS_CLOSED and not is_organizer:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"detail": "This group buy is closed."}, status=400)
        messages.error(request, "This group buy is closed. Only the organizer can remove items.")
        return redirect("groupbuy_detail", groupbuy_id=groupbuy_id)

    item.delete()
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"deleted": True})
    messages.success(request, "Item removed.")
    return redirect("groupbuy_detail", groupbuy_id=groupbuy_id)

@login_required
@require_POST
def join_groupbuy(request, groupbuy_id):
    # Join a group buy by creating or updating the user's order (idempotent per user+groupbuy).
    groupbuy = get_object_or_404(GroupBuy, id=groupbuy_id)

    if groupbuy.status != GroupBuy.STATUS_OPEN:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"detail": "This group buy is not open."}, status=400)
        messages.error(request, "This group buy is not open for joining.")
        return redirect("groupbuy_detail", groupbuy_id=groupbuy_id)

    raw_quantity = (request.POST.get("quantity") or "").strip()
    try:
        quantity = int(raw_quantity)
    except (ValueError, TypeError):
        quantity = None

    if quantity is None or quantity <= 0:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"detail": "Please enter a valid quantity."}, status=400)
        messages.error(request, "Please enter a valid quantity.")
        return redirect("groupbuy_detail", groupbuy_id=groupbuy_id)

    try:
        with transaction.atomic():
            Order.objects.update_or_create(
                user=request.user,
                groupbuy=groupbuy,
                defaults={"quantity": quantity},
            )
    except IntegrityError:
        existing_order = Order.objects.filter(user=request.user, groupbuy=groupbuy).order_by("-id").first()
        if existing_order:
            existing_order.quantity = quantity
            existing_order.save(update_fields=["quantity"])
        else:
            Order.objects.create(user=request.user, groupbuy=groupbuy, quantity=quantity)

    return redirect("groupbuy_detail", groupbuy_id=groupbuy_id)


@login_required
def my_orders(request):
    # List the current user's orders with optional category filtering.

    selected_category = (request.GET.get("category") or "").strip()
    orders = Order.objects.filter(user=request.user).select_related("groupbuy").order_by("-id")
    if selected_category and selected_category in dict(GroupBuy.CATEGORY_CHOICES):
        orders = orders.filter(groupbuy__category=selected_category)
    for order in orders:
        order.total_price = (order.groupbuy.price * Decimal(order.quantity)).quantize(Decimal("0.01"))

    return render(request, "my_orders.html", {
        "orders": orders,
        "selected_category": selected_category,
        "category_choices": GroupBuy.CATEGORY_CHOICES,
    })

@login_required
@require_POST
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.delete()
    messages.success(request, "Order removed.")
    return redirect("my_orders")


@login_required
def profile_view(request):
    # Render the profile page for the current user.

    return render(request, "profile.html")


@require_POST
def logout_view(request):
    # Log the current user out.

    logout(request)

    return redirect("login")

