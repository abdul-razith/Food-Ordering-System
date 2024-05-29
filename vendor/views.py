from django.shortcuts import render, redirect
from django.http import JsonResponse
from Food.models import CheckOut, Item
from users.models import profile
from .models import *
from .forms import *
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime, timedelta, date
from django.db.models import Sum
from django.core.paginator import Paginator
from django.db.models import Q



# Create your views here.

def home(request):
    """
    data = CheckOut.objects.all().order_by('-order_at')[:3]
    context = {
        'data': data
        } """

    
    # Income
    today = datetime.now()
    seven_days_ago = today - timedelta(days=7)
    one_month_ago = today - timedelta(days=30)
    six_months_ago = today - timedelta(days=180)  # Assuming 30 days per month
    one_year_ago = today - timedelta(days=365)

    today_income = OrdersRecords.objects.filter(
        order_at__icontains=date.today()
    ).aggregate(total_income=Sum('total'))['total_income'] or 0

    one_month_income = OrdersRecords.objects.filter(
        order_at__range=(one_month_ago, today)
    ).aggregate(total_income=Sum('total'))['total_income'] or 0

    six_months_income = OrdersRecords.objects.filter(
        order_at__range=(six_months_ago, today)
    ).aggregate(total_income=Sum('total'))['total_income'] or 0

    last_year_income = OrdersRecords.objects.filter(
        order_at__range=(one_year_ago, today)
    ).aggregate(total_income=Sum('total'))['total_income'] or 0

    # Order Status
    process = CheckOut.objects.filter(delivered_status = 0, order_at__icontains = date.today()).count()
    out = CheckOut.objects.filter(delivered_status = 1, order_at__icontains = date.today()).count()
    delivered = CheckOut.objects.filter(delivered_status = 2, order_at__icontains = date.today()).count()

    # Completed Orders
    completed_orders_count = delivered
    today_orders = OrdersRecords.objects.filter(order_at__icontains = date.today()).count()
    one_month_orders = OrdersRecords.objects.filter(order_at__range = (one_month_ago, today)).count()
    six_months_orders = OrdersRecords.objects.filter(order_at__range = (six_months_ago, today)).count()
    one_year_orders = OrdersRecords.objects.filter(order_at__range = (one_year_ago, today)).count()

    context = {
        # Orders Status
        'process' : process,
        'out' : out,
        'delivered' : delivered,
        #'completed_orders' : completed_orders_count,

        # Income
        'today_income': today_income,
        'one_month_income': one_month_income,
        'six_months_income': six_months_income,
        'last_year_income': last_year_income,

        # Completed Orders
        'today_orders' : today_orders,
        'one_month_orders' : one_month_orders,
        'six_months_orders' : six_months_orders,
        'one_year_orders' : one_year_orders,
    }
    return render(request, 'vendor/restaurant-dashboard.html', context)

def delivery_status(request, userid, orderid):
    if request.method == 'POST':
        #checkout_id = request.POST.get('checkout_id')
        delivery_status = request.POST.get('delivery_status')

        # Map delivery status to corresponding database values
        delivery_status_mapping = {
            'In Progress': 0,
            'Out for Delivery': 1,
            'Delivered': 2
        }

        if delivery_status in delivery_status_mapping:
            status_code = delivery_status_mapping[delivery_status]
            # Update delivery status in the database

            try:
                checkout = CheckOut.objects.get(id=orderid)
                checkout.delivered_status = status_code
                checkout.save()
                if status_code == 2:
                    record = OrdersRecords()
                    if not OrdersRecords.objects.filter(order_id=checkout.id).exists():
                        record.order_id = checkout.id
                        record.user_id = checkout.user_id
                        record.user_name = checkout.user_name
                        record.cart_items = checkout.cart_items
                        record.total = checkout.final_price
                        record.order_at = checkout.order_at
                        record.save()
                        #CheckOut.objects.get(id = orderid).delete()
            except CheckOut.DoesNotExist:
                # Handle case where checkout does not exist
                pass
            
    return redirect('vendor:order')  # Redirect to the checkout page after updating delivery status

def single(request, userid, orderid):

    # Retrieve profile data for the specified user ID
    profile_data = profile.objects.filter(user_id=userid).first()

    if profile_data:
        name = profile_data.user
        mobileno = profile_data.mobile_no1
        address = profile_data.address
        city = profile_data.city
        state = profile_data.state
        profile_img = profile_data.image

        # Create profile dictionary
        profile_dict = {
            'name': name,
            'mobileno': mobileno,
            'address': address,
            'city': city,
            'state': state,
            'profile_img': profile_img
        }
    else:
        profile_dict = {}


    # Retrieve checkout data for the specified user ID
    checkout_data = CheckOut.objects.filter(id=orderid).first()

    if checkout_data:
        # Extract relevant fields from the checkout data
        shipping_price = checkout_data.shipping_price
        sub_total = checkout_data.sub_total
        final_price = checkout_data.final_price

        status = checkout_data.delivered_status

        # Extract cart items from checkout data
        cart_items_json = checkout_data.cart_items
        cart_items_dict_list = json.loads(cart_items_json)

        # Initialize a list to hold the final cart items data
        cart_items_list = []

        # Iterate over each cart item
        for item_dict in cart_items_dict_list:
            item_id = item_dict.get('id')
            quantity = item_dict.get('quantity')
            try:
                # Retrieve item details from Item model
                item = Item.objects.get(pk=item_id)
                if item.discount > 0:
                    item_price = item.item_price - (item.item_price * item.discount / 100)
                else:
                    item_price = item.item_price
                
                org_price = item.item_price
                discount = item.discount
                item_price =  org_price - (org_price * discount / 100)
                total = item_price * quantity

                item_details = {
                    'name': item.item_name,
                    'img': item.item_image,
                    'price': item_price,

                    'quantity': quantity,
                    'total': total,

                    'discount' : item.discount,
                }
                cart_items_list.append(item_details)
            except Item.DoesNotExist:
                # Handle case where item does not exist
                pass

        # Create context with profile and cart items data
        context = {
            'data': profile_dict,
            'shipping_price': shipping_price,
            'sub_total': sub_total,
            'final_price': final_price,
            'items_list': cart_items_list,
            'user_id': userid,
            'order_id': orderid,

            'status': status,
        }
    else:
        # Create context only with profile data
        context = {'data': profile_dict}

    return render(request, 'vendor/single.html', context)

def history_single(request, userid, orderid):

    # Retrieve profile data for the specified user ID
    profile_data = profile.objects.filter(user_id=userid).first()

    if profile_data:
        name = profile_data.user
        mobileno = profile_data.mobile_no1
        address = profile_data.address
        city = profile_data.city
        state = profile_data.state
        profile_img = profile_data.image

        # Create profile dictionary
        profile_dict = {
            'name': name,
            'mobileno': mobileno,
            'address': address,
            'city': city,
            'state': state,
            'profile_img': profile_img
        }
        print("uppers \t", profile_dict)
    else:
        profile_dict = {}
        print("downs \t", profile_dict)

    # Retrieve checkout data for the specified user ID
    checkout_data = CheckOut.objects.filter(id=orderid).first()

    if checkout_data:
        # Extract relevant fields from the checkout data
        shipping_price = checkout_data.shipping_price
        sub_total = checkout_data.sub_total
        final_price = checkout_data.final_price

        status = checkout_data.delivered_status

        # Extract cart items from checkout data
        cart_items_json = checkout_data.cart_items
        cart_items_dict_list = json.loads(cart_items_json)

        # Initialize a list to hold the final cart items data
        cart_items_list = []

        # Iterate over each cart item
        for item_dict in cart_items_dict_list:
            item_id = item_dict.get('id')
            quantity = item_dict.get('quantity')
            try:
                # Retrieve item details from Item model
                item = Item.objects.get(pk=item_id)
                if item.discount > 0:
                    item_price = item.item_price - (item.item_price * item.discount / 100)
                else:
                    item_price = item.item_price
                
                org_price = item.item_price
                discount = item.discount
                item_price =  org_price - (org_price * discount / 100)
                total = item_price * quantity

                item_details = {
                    'name': item.item_name,
                    'img': item.item_image,
                    'price': item_price,

                    'quantity': quantity,
                    'total': total,

                    'discount' : item.discount,
                }
                cart_items_list.append(item_details)
            except Item.DoesNotExist:
                # Handle case where item does not exist
                pass

        # Create context with profile and cart items data
        context = {
            'data': profile_dict,
            'shipping_price': shipping_price,
            'sub_total': sub_total,
            'final_price': final_price,
            'items_list': cart_items_list,
            'user_id': userid,
            'order_id': orderid,

            'status': status,
        }
        print("loki \t", profile_dict)
    else:
        # Create context only with profile data
        context = {'data': profile_dict}
        print("last \t", profile_dict)

    return render(request, 'vendor/history-single.html', context)

# Menu builder home page with food items.
def menu_builder(request):
    if request.method == 'POST':
        search = request.POST.get('food_name')

        try:
            search_id = int(search)
            data = Item.objects.filter(id=search_id)
        except ValueError:
            data = Item.objects.filter(item_name__icontains=search)

        paginator = Paginator(data, 15)
        page = request.GET.get('page')
        data = paginator.get_page(page)
        
        return render(request, 'vendor/menu-builder.html', {'data': data})
    else:
        data = Item.objects.all()
        paginator = Paginator(data, 15)
        page = request.GET.get('page')
        data = paginator.get_page(page)
        
        return render(request, 'vendor/menu-builder.html', {'data': data})


# Add new food item
def add_food(request):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('vendor:menubuilder')
            # Redirect or display success message
    else:
        form = ItemForm()
    return render(request, 'vendor/add-food.html', {'form': form})

def update_food(request, id):
    item_instance = Item.objects.get(id=id)
    form = ItemForm(request.POST or None, request.FILES or None, instance=item_instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('vendor:menubuilder')  # Redirect to a success URL after saving the form
    return render(request, 'vendor/update-food.html', {'form': form})


def delete_food(request, id):
    Item.objects.get(id=id).delete()
    return redirect('vendor:menubuilder')

def order(request):
    if request.method == "POST":
        oid = request.POST.get('oid')
        try:
            #data = CheckOut.objects.get(id=oid)
            data = CheckOut.objects.filter(id=oid).exclude(delivered_status=2).first()
        except CheckOut.DoesNotExist:
            # Handle the case where the object is not found
            return render(request, 'vendor/restaurant-order-details.html')
        #data = CheckOut.objects.get(id = oid)

        return render(request, 'vendor/restaurant-order-details.html', {'data' : data})
    else:
        #data = CheckOut.objects.filter(delivered_status = 2)
        #data = CheckOut.objects.all().order_by('-order_at')
        data = CheckOut.objects.exclude(delivered_status = 2).order_by('-order_at')

        # Pagination
        paginator = Paginator(data, 8)
        page = request.GET.get('page')
        data = paginator.get_page(page)


        return render(request, 'vendor/restaurant-order.html', {'data' : data})

def orders_history(request):
    if request.method == "POST":
        oid = request.POST.get('oid')
        try:
            data = OrdersRecords.objects.get(order_id = oid)
        except OrdersRecords.DoesNotExist:
            return render(request, 'vendor/restaurant-orders-history-details.html')
            pass
        data = OrdersRecords.objects.get(order_id = oid)
        
        
        return render(request, 'vendor/restaurant-orders-history-details.html', {'data':data})   
    else:
        data = OrdersRecords.objects.all().order_by('-id')

        #pagination
        paginator = Paginator(data, 10)
        page = request.GET.get('page')
        data = paginator.get_page(page)

        context = {
            'data' : data
        }
        return render(request, 'vendor/restaurant-orders-history.html', context)
