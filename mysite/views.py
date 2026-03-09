
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from groupbuy.models import GroupBuy, Order


@login_required
def dashboard(request):

    groupbuys = GroupBuy.objects.all()

    return render(request, "dashboard.html", {
        "groupbuys": groupbuys
    })


@login_required
def create_groupbuy(request):

    if request.method == "POST":

        title = request.POST["title"]
        description = request.POST["description"]
        price = request.POST["price"]
        target_quantity = request.POST["target_quantity"]

        GroupBuy.objects.create(
            title=title,
            description=description,
            price=price,
            target_quantity=target_quantity,
            created_by=request.user
        )

        return redirect("dashboard")

    return render(request, "create_groupbuy.html")

def login_view(request):


    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:

            login(request, user)

            return redirect("dashboard")

    return render(request, "login.html")
    
def register_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        if not User.objects.filter(username = username).exists():
            User.objects.create_user(
            username=username,
            password=password
        )

        return redirect("login")

    return render(request, "register.html")


@login_required
def groupbuy_detail(request, groupbuy_id):

    groupbuy = get_object_or_404(GroupBuy, id=groupbuy_id)

    orders = Order.objects.filter(groupbuy=groupbuy)

    return render(request, "detail.html", {
        "groupbuy": groupbuy,
        "orders": orders
    })


@login_required
def join_groupbuy(request, groupbuy_id):
    if request.method == "POST":
        groupbuy = get_object_or_404(GroupBuy, id=groupbuy_id)

        quantity = request.POST["quantity"]

        Order.objects.create(
            user=request.user,
            groupbuy=groupbuy,
            quantity=quantity
        )

    return redirect("groupbuy_detail", groupbuy_id=groupbuy_id)


@login_required
def my_orders(request):

    orders = Order.objects.filter(user=request.user)

    return render(request, "my_orders.html", {
        "orders": orders
    })


@login_required
def profile_view(request):

    return render(request, "profile.html")


def logout_view(request):

    logout(request)

    return redirect("login")

