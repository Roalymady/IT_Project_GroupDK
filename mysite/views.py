from django.shortcuts import render, redirect


def dashboard(request):
    return render(request, "dashboard.html")


def create_groupbuy(request):
    if request.method == "POST":
        return redirect("groupbuy_detail", groupbuy_id=1)
    return render(request, "create_groupbuy.html")


def login_view(request):
    if request.method == "POST":
        return redirect("dashboard")
    return render(request, "login.html")


def register_view(request):
    if request.method == "POST":
        return redirect("dashboard")
    return render(request, "register.html")


def groupbuy_detail(request, groupbuy_id):
    return render(request, "detail.html", {"groupbuy_id": groupbuy_id})


def my_orders(request):
    return render(request, "my_orders.html")


def logout_view(request):
    return redirect("login")


def profile_view(request):
    return render(request, "profile.html")
