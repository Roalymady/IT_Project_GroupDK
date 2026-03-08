
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [

    path('admin/', admin.site.urls),

    path('', views.dashboard, name="dashboard"),

    path('login/', views.login_view, name="login"),

    path('register/', views.register_view, name="register"),

    path('logout/', views.logout_view, name="logout"),

    path('create/', views.create_groupbuy, name="create_groupbuy"),

    path('groupbuy/<int:groupbuy_id>/', views.groupbuy_detail, name="groupbuy_detail"),

    path('groupbuy/<int:groupbuy_id>/join/', views.join_groupbuy, name="join_groupbuy"),

    path('orders/', views.my_orders, name="my_orders"),

    path('profile/', views.profile_view, name="profile"),
]

"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path

from .views import (
    dashboard,
    create_groupbuy,
    login_view,
    register_view,
    groupbuy_detail,
    my_orders,
    logout_view,
    profile_view,
)

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("groupbuys/create/", create_groupbuy, name="create_groupbuy"),
    path("groupbuys/<int:groupbuy_id>/", groupbuy_detail, name="groupbuy_detail"),
    path("orders/", my_orders, name="my_orders"),
    path("profile/", profile_view, name="profile"),
    path("logout/", logout_view, name="logout"),
    path("admin/", admin.site.urls),
]
