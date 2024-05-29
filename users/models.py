from django.db import models
from django.core.validators import MaxLengthValidator
from django.contrib.auth.models import User, AbstractUser
# Create your models here.

class CustomUser(AbstractUser):
    email = models.EmailField(max_length = 100, unique = True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

class profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    image = models.ImageField(default='profile_pic.jpg', upload_to='profile_images')

    mobile_no1 = models.CharField(max_length=10, validators=[MaxLengthValidator(10, message="Mobile number must be 10 digits long")])
    #mobile_no2 = models.CharField(max_length=10, validators=[MaxLengthValidator(10, message="Mobile number must be 10 digits long")])
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50, null=True)
    state = models.CharField(max_length=20, null=True)
    pin_code = models.CharField(max_length=6, validators=[MaxLengthValidator(6, message="Enter a valid PIN code")])
    land_mark = models.CharField(max_length=50, null=True)
    user_review = models.TextField(max_length = 200, null = True)


    def __str__(self):
        return self.user.username