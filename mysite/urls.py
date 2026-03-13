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

    path('groupbuy/<int:groupbuy_id>/add-item/', views.add_groupbuy_item, name="add_groupbuy_item"),

    path('groupbuy/<int:groupbuy_id>/items/<int:item_id>/delete/', views.delete_groupbuy_item, name="delete_groupbuy_item"),

    path('groupbuy/<int:groupbuy_id>/status/', views.update_groupbuy_status, name="update_groupbuy_status"),

    path('groupbuy/<int:groupbuy_id>/delete/', views.delete_groupbuy, name="delete_groupbuy"),

    path('orders/', views.my_orders, name="my_orders"),

    path('orders/<int:order_id>/delete/', views.delete_order, name="delete_order"),

    path('profile/', views.profile_view, name="profile"),
]
