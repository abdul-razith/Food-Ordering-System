from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
#from django.contrib.auth.models import User
from datetime import datetime
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class Item(models.Model):
    category1 = {
    # Veg category
    'veg': 'Veg',
    '_line_veg': '--------------------------------',
    'pizza': 'Pizza',
    'fullmeals_veg': 'Full Meals',
    'burgers': 'Burgers',
    'pasta': 'Pasta',
    'salads': 'Salads',
    #'sandwiches': 'Sandwiches',
    'wraps': 'Wraps',

    # Non-Veg category
    '_line_nonveg': '--------------------------------',
    'nonveg': 'Non - Veg',
    '_line_nonvegs': '--------------------------------',
    'fry': 'Fry',
    'fullmeals_nonveg': 'Full Meals',
    'bbq': 'BBQ Items',
    'grilled': 'Grilled Meats',
    'curries': 'Curries',
    'soups': 'Soups',
    'chicken': 'Chicken Specialties',

    # Sea food category
    '_line_seafood': '--------------------------------',
    'seafood': 'Sea Food',
    '_line_seafoods': '--------------------------------',
    'fry_seafood': 'Fry Varieties',
    'curry_seafood': 'Curry Specialties',
    'grilled_seafood': 'Grilled Delights',
    'stew_and_soups_seafood': 'Stew and Soups',
    }

    category2 = {
        'veg':'Veg',
        'non-veg':'Non - Veg',
        'seafood':'Sea Food'
    }

    user_name = models.ForeignKey(User, on_delete=models.CASCADE,default=1)
    item_name = models.CharField(max_length=60)
    item_desc = models.CharField(max_length=100)
    item_price = models.IntegerField()
    #item_image = models.CharField(max_length=500, default="https://www.fnasafety.com/wp-content/uploads/2016/04/ComingSoon2-fnasafety.png")
    item_image = models.ImageField(default='food_pic.png', upload_to='food_images')
    
    item_category = models.CharField(max_length=50, choices = category1, default = None)
    sub_category = models.CharField(max_length=10, choices = category2, default = None)
    is_trending = models.BooleanField(default=False)
    discount = models.IntegerField(default = 0,
        validators = [
            MinValueValidator(limit_value=0, message="The value must be greater than or equal to 0."),
            MaxValueValidator(limit_value=100, message="The value must be less than or equal to 100")
        ]
    )

    def __str__(self):
        return self.item_name
    
    """
    This method is used to redirect to the another page, after the 'new item' is created.
    The reverse method contains 'template name and pk in dict format' "kwargs={"pk":self.pk}".
    """
    def get_absolute_url(self):
        return reverse("Food:detail", kwargs={"pk":self.pk})
    

class Cart(models.Model):
    user_name = models.CharField(max_length=30)
    user_id = models.PositiveIntegerField()
    food_id = models.IntegerField()
    #food_image = models.CharField(max_length=500)
    food_image = models.ImageField(default='food_pic.png', upload_to='food_images')
    food_name = models.CharField(max_length=30)
    food_price = models.PositiveIntegerField()

    food_discount = models.PositiveIntegerField(default = 0) # Specfic food discount percentage eg: 10 %.
    food_discount_price = models.PositiveIntegerField(null = True) # After discount of the food price (specfic food).
    food_price_saved = models.PositiveIntegerField(default = 0) # Amount saved in the discount for the specfic food.

    food_quantity = models.IntegerField(default=1)
    total = models.IntegerField(default = None)

    def __str__(self):
        return self.user_name

class CheckOut(models.Model):
    user_id = models.IntegerField()
    user_name = models.CharField(max_length=30)
    cart_items = models.JSONField()  # Store cart items as JSON data
    sub_total = models.IntegerField()
    shipping_price = models.IntegerField()
    final_price = models.IntegerField()
    #discounted_price = models.IntegerField(null=True)
    order_at = models.DateTimeField(auto_now_add=True)
    delivered_status = models.IntegerField(default = 0)

    def __str__(self):
        return self.user_name
