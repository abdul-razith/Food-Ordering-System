from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import *
from Food.models import *
from django.contrib.auth import get_user_model
import json
import re


User = get_user_model()

from .forms import RegisterForm
# Create your views here.
def signout(request):
    logout(request)
    return redirect('Food:index')


def custom_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password1')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You have been successfully logged in.')
            return redirect('Food:index')  # Redirect to the dashboard or any other page after login
        else:
            #messages.error(request, 'Invalid username or password. Please try again.')
            return render(request, 'users/login.html', {'error_message': 'Invalid username or password.'})
    else:
        return render(request, 'users/login.html')

def register(request):
    if request.method == "POST":
        email = request.POST.get('email')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Check if email is None or empty
        if not email:
            messages.error(request, "Email is required.")
            return redirect('register')

        # Check if email is already registered
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect('register')

        # Check if username is already taken
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return redirect('register')

        # Check if passwords match
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register')
        
        # Check if password length is greater than 8 characters
        if len(password1) < 8:
            messages.error(request, "Password must have more than 8 characters.")
            return redirect('register')

        # Create new user
        user = CustomUser(email=email, username=username)
        user.set_password(password1)

        if 'admin' in email:
            user.is_staff = True
            user.is_superuser = True

        user.save()

        messages.success(request, f"Welcome {username}, your account is created.")
        return redirect("login")
    else:
        return render(request, "users/register.html")


@login_required
def profile_fun(request):
    user_id = request.user.id
    data = CheckOut.objects.filter(user_id = user_id).exclude(delivered_status = 9).order_by('-order_at')[:5]
    print(data)
    return render(request, 'users/profile.html', {'data' : data})

def update_profile(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            id = request.user.id
            firstname = request.POST.get('firstname')
            lastname = request.POST.get('lastname')
            mobileno1 = request.POST.get('mobileno1')
            #mobileno2 = request.POST.get('mobileno2')
            address = request.POST.get('address')
            city = request.POST.get('city')
            state = request.POST.get('state')
            pincode = request.POST.get('pincode')
            landmark = request.POST.get('landmark')
            review = request.POST.get('review')
            
            request.user.first_name = firstname
            request.user.last_name = lastname
            request.user.save()

            

            pro = profile.objects.get(user_id = id)
            pro.mobile_no1 = mobileno1
            #pro.mobile_no2 = mobileno2
            pro.address = address
            pro.city = city
            pro.state = state
            pro.pin_code = pincode
            pro.land_mark = landmark
            pro.user_review = review

            # Handle profile picture update
            if 'profilepic' in request.FILES:
                profile_pic = request.FILES['profilepic']
                # Save the uploaded image to the local storage
                pro.image.save(profile_pic.name, profile_pic)
                
            pro.save()

            from_page = request.GET.get('from', '')
            if from_page == 'profile':
                return redirect('profile')
            else:
                return redirect('Food:endpage')
    else:
        return render(request, 'users/login.html')

def single(request, userid, orderid):

    # Retrieve profile data for the specified user ID
    profile_data = profile.objects.filter(id=userid).first()

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
            'profile_img': profile_img,
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
        order_at = checkout_data.order_at

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

                org_price = item.item_price
                discount = item.discount
                item_price =  org_price - (org_price * discount / 100)
                total = item_price * quantity
                print(item_price, quantity, total)
                
                item_details = {
                    'name': item.item_name,
                    'img': item.item_image,
                    'price': item_price,

                    'quantity': quantity,
                    'total': total

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
            'order_at' : order_at,
            'items_list': cart_items_list,
            'user_id': userid,
            'order_id': orderid,

            'status': status,
        }
    else:
        # Create context only with profile data
        context = {'data': profile_dict}

    return render(request, 'users/one.html', context)
