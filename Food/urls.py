from django.contrib import admin
from django.urls import path
from Food import views

app_name = 'Food'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='index'),
    path('menu', views.menu, name='menu'),
    path('menuveg', views.menu_veg, name='menuveg'),
    path('menunonveg', views.menu_nonveg, name='menunonveg'),
    path('menusea', views.menu_sea, name='menusea'),

    path('addtocart/', views.add_to_cart, name='addtocart'),
    path('tempcart/', views.temp_cart, name='tempcart'),
    path('removecart/<int:item_id>/', views.remove_from_cart, name='removecart'),
    path('updatecart', views.update_cart, name='updatecart'),
    path('checkout', views.checkout, name='checkout'),
    path('endpage', views.end_page, name='endpage'),
    path('placeorder/<int:orderid>/', views.place_order, name='placeorder'),
    path('cancelorder/<int:orderid>/', views.cancel_order, name='cancelorder'),
    path('clearcart/<int:userid>/', views.clear_cart, name='clearcart'),


    path('book', views.book, name='book'),
    path('about', views.about, name='about'),
]
