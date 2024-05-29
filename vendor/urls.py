from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.auth import views as auth_views
from vendor import views as users_views


app_name = 'vendor'

urlpatterns = [
    path('', users_views.home, name='index'),

    path('single/<int:userid>/<int:orderid>/', users_views.single, name='single'),
    path('historysingle/<int:userid>/<int:orderid>/', users_views.history_single, name='historysingle'),
    path('delivery_status/<int:userid>/<int:orderid>/', users_views.delivery_status, name='deliverystatus'),

    path('menubuilder', users_views.menu_builder, name='menubuilder'),
    path('addfood', users_views.add_food, name='addfood'),
    path('updatefood/<str:id>/', users_views.update_food, name='updatefood'),
    path('deletefood/<int:id>/', users_views.delete_food, name='deletefood'),

    path('order', users_views.order, name='order'),
    path('ordershistory', users_views.orders_history, name='ordershistory'),
]
