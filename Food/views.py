from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse
from .models import *
from users.models import *
from django.http import HttpResponse
from django.http import JsonResponse, HttpResponseRedirect
import json
from .forms import Itemform
from django.contrib import messages
from django.contrib.auth import get_user_model
from datetime import datetime as dt
from django.contrib import messages
User = get_user_model()

#-----------------------------

# Create your views here.

def home(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or 'admin' in request.user.email:
            # Skip user reviews for superusers or users with 'admin' in their email
            review = profile.objects.exclude(user=request.user).exclude(user_review=None).distinct()
            #data = CheckOut.objects.all().order_by('-order_at')[:3]
            #context = {
            #    'data': data
            #}
            #return render(request, 'vendor/restaurant-dashboard.html', context)
            return redirect('vendor:index')
        else:
            review = profile.objects.exclude(user_review=None).distinct()
        
        data = Item.objects.filter(is_trending=True)
        offer = Item.objects.filter(discount__gt=0, is_trending=True)[:8]
        context = {
            'data': data,  # Send trending foods
            #'menu1': Item.category1,  # Send food types names
            #'menu2' : Item.category2, # veg or no-veg
            'menu1': {
            'pizza': 'Pizza',
            'pasta': 'Pasta',
            'chicken': 'Chicken Specialties',
            'curries': 'Curries',
            'grilled_seafood': 'Grilled Delights',
            'wraps': 'Wraps',
            },
            
            'offer': offer,  # Send offer foods
            'review': review  # Send user reviews
        }
    else:
        data = Item.objects.filter(is_trending=True)
        offer = Item.objects.filter(discount__gt=0, is_trending=True)[:8]
        review = profile.objects.exclude(user_review=None).distinct()
        context = {
            'data': data,  # Send trending foods
            'menu1': {
            'pizza': 'Pizza',
            'pasta': 'Pasta',
            'chicken': 'Chicken Specialties',
            'curries': 'Curries',
            'grilled_seafood': 'Grilled Delights',
            'wraps': 'Wraps',
            },
            'offer': offer,  # Send offer foods
            'review': review  # Send user reviews
        }
    
    return render(request, "Food/index.html", context)


def book(request):
    return render(request, "Food/book.html")

def menu(request):
    """
    data = Item.objects.all()

    if request.method == 'POST':
        item = request.POST.get('food_name')
        data = Item.objects.filter(item_name__contains = item)
    context = {
        'data' : data, # its send all foods.
        'menu1' : Item.category1, # its send food types name.
        #'menu2' : Item.category2, # veg or no-veg
    }
    """
    return render(request, "Food/menu.html")

def menu_veg(request):
    data = Item.objects.filter(sub_category = 'veg')

    context = {
        'data' : data, # its send all foods.
        'menu1': {
            'pizza': 'Pizza',
            'fullmeals_veg': 'Full Meals',
            'burgers': 'Burgers',
            'pasta': 'Pasta',
            'salads': 'Salads',
            'wraps': 'Wraps',
        }
    }
    return render(request, "Food/menu-veg.html", context)

def menu_nonveg(request):
    data = Item.objects.filter(sub_category = 'non-veg')

    if request.method == 'POST':
        item = request.POST.get('non-veg')
        data = Item.objects.filter(item_name__contains = item)
    context = {
        'data' : data, # its send all foods.
        'menu1': {
            'fry': 'Fry',
            'fullmeals_nonveg': 'Full Meals',
            'bbq': 'BBQ Items',
            'grilled': 'Grilled Meats',
            'curries': 'Curries',
            'soups': 'Soups',
            'chicken': 'Chicken Specialties',
        }
    }
    return render(request, "Food/menu-nonveg.html", context)

def menu_sea(request):
    data = Item.objects.filter(sub_category = 'seafood')

    if request.method == 'POST':
        item = request.POST.get('food_name')
        data = Item.objects.filter(item_name__contains = item)
    context = {
        'data' : data, # its send all foods.
        'menu1': {
            'fry_seafood': 'Fry Varieties',
            'curry_seafood': 'Curry Specialties',
            'grilled_seafood': 'Grilled Delights',
            'stew_and_soups_seafood': 'Stew and Soups',
        }
    }
    return render(request, "Food/menu-sea.html", context)


def search(request):

    if request.method == 'POST':
        value = request.POST.get('food_name')
        datas = Item.objects.filter(item_name__icontains = value)
    
        context = {
            'data' : datas,
        }
        return render(request, 'Food/search.html', context)
    return render(request, 'Food/search.html')

# This method is used to add a foods, if the user click the cart button using ajax request.
def add_to_cart(request):
    if request.user.is_authenticated:
        data = json.load(request)
        pid = data['pid']
        pobj = Item.objects.get(pk=pid)

        item_count = Cart.objects.filter(user_id=request.user.id).count()
        if item_count <= 6:
            if Cart.objects.filter(user_id=request.user.id, food_name=pobj.item_name).exists():
                return JsonResponse({'status' : 'Food item is already in cart.'})
            else:
                tc = Cart()

                food_price = pobj.item_price
                discount = pobj.discount
                food_discount_price = food_price - (food_price * discount / 100) # After discount
                food_discount_saved = food_price - food_discount_price

                tc.user_name = request.user.username
                tc.user_id = request.user.id
                tc.food_id = pid
                tc.food_image = pobj.item_image
                tc.food_name = pobj.item_name
                #tc.food_price = pobj.item_price
                tc.food_price = food_price

                tc.food_discount = discount
                tc.food_discount_price = food_discount_price
                tc.food_price_saved = food_discount_saved
                tc.total = tc.food_quantity * food_discount_price
                tc.save()
        else:
            return JsonResponse({'message': 'Cart is full.'})

        #return JsonResponse({'message': 'Item added to cart successfully!'})
        return render(request, 'Food/cart_new.html'), JsonResponse({'message': 'Item added to cart successfully!'})
    else:
        #messages.error(request, 'Please Login')
        return JsonResponse({'message': 'Please Login to add food in the cart.'},status=401)
    
@login_required
def temp_cart(request):
    id = request.user.id
    data = Cart.objects.filter(user_id = id)
    context = {
        'data' : data
    }
    #print(data)
    return render(request, 'Food/cart_new.html', context)


# This is used to delete the specfic item from the cart.
def remove_from_cart(request, item_id):
    if request.method == 'POST':
        Cart.objects.filter(id=item_id).delete()
        return redirect('Food:tempcart')



def update_cart(request):
    if request.user.is_authenticated and request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart_items = data.get('cartItems', [])
            #subtotal = data.get('subtotal')
            
            for item_data in cart_items:
                item_id = item_data.get('id')
                quantity = item_data.get('quantity')
                
                # Update the cart item with the given item_id and user_id
                cart_item = Cart.objects.get(food_id=item_id, user_id=request.user.id)
                cart_item.food_quantity = quantity
                cart_item.total = cart_item.food_discount_price * float(quantity)
                cart_item.save()
            
            return JsonResponse({'message': 'Cart items updated successfully'})

        except KeyError:
            return JsonResponse({'error': 'Invalid data format'}, status=400)

        except Cart.DoesNotExist:
            return JsonResponse({'error': 'Cart item does not exist'}, status=404)

    else:
        return JsonResponse({'error': 'Unauthorized access or invalid request method'}, status=401)

def checkout(request):
    if request.user.is_authenticated and request.method == 'POST':
        data = json.loads(request.body)
        cart_items = data.get('cartItems', [])
        subtotal = data.get('subtotal')
        shipping = data.get('shipping')
        finaltotal = data.get('finaltotal')

        # Serialize cart items as JSON data
        cart_data = json.dumps(cart_items)
        

        # Check if a checkout entry already exists for the current user and cart items
        if CheckOut.objects.filter(user_id=request.user.id, cart_items=cart_data).exists():
            response_data = {'error': 'Checkout entry already exists'}
            return JsonResponse(response_data, status=400)

        try:
            # Create a new checkout entry for the current user
            checkout_entry = CheckOut.objects.create(
                user_id=request.user.id,
                user_name=request.user.username,
                cart_items=cart_data,
                sub_total=float(subtotal),
                shipping_price=shipping,
                final_price=float(finaltotal)
            )
            #print("Created new checkout entry for user:", request.user.id)

            response_data = {'message': 'Checkout successful'}
            return JsonResponse(response_data)

        except Exception as e:
            #print("Error:", e)
            return JsonResponse({'error': 'An error occurred while processing the request'}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)

def end_page(request):
    if request.user.is_authenticated:
        #sub_total = 0
        #shipping_price = 0
        #final_total = 0

        user_id = request.user.id
        #data = CheckOut.objects.filter(user_id = user_id)
        #data = Cart.objects.filter(user_id=user_id).order_by('-order_at')
        data = Cart.objects.filter(user_id=user_id)
        data1 = CheckOut.objects.filter(user_id = user_id)
        for co_data in data1:
            sub_total = co_data.sub_total
            shipping_price = co_data.shipping_price
            final_total = co_data.final_price
            order_id = co_data.id
        #print(sub_total, shipping_price, final_total)
        context = {
            'data' : data,

            'sub_total' : sub_total,
            'shipping_price' : shipping_price,
            'final_total' : final_total,
            'order_id': order_id,
        }
        return render(request, 'Food/checkout_new.html', context)
    else:
        return render(request, 'Food/checkout_new.html')


# This fn is used to delete the specific user cart items after finishing the shopping.
def place_order(request, orderid):
    if request.user.is_authenticated:
        user_id = request.user.id
        Cart.objects.filter(user_id=user_id).delete()
        co = CheckOut.objects.get(id = orderid)
        co.delivered_status = 0
        co.save()
        # CheckOut.objects.filter(user_id=user_id).delete()
        #print("Deleted")
        messages.success(request, "Order is succussfull. Please check your profile.")
        return redirect("Food:index")
    
def cancel_order(request, orderid):
    if request.user.is_authenticated:
        user_id = request.user.id
        Cart.objects.filter(user_id=user_id).delete()
        CheckOut.objects.get(id=orderid).delete()

        #print("Deleted")
        messages.success(request, "Order is cancelled.")
        return redirect("Food:index")
    
def clear_cart(request, userid):
    Cart.objects.filter(user_id = userid).delete()
    return redirect("Food:tempcart")

def about(request):
    return render(request, "Food/about.html")