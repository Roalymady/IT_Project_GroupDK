
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

    path('groupbuy/<int:groupbuy_id>/delete/', views.delete_groupbuy, name="delete_groupbuy"),

    path('orders/', views.my_orders, name="my_orders"),

    path('profile/', views.profile_view, name="profile"),
]
