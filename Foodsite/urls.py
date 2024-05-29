"""
URL configuration for Foodsite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.auth import views as auth_views
from users import views as users_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('Food/', include('Food.urls')),
    path('vendor/', include('vendor.urls')),
    
    path('login/', users_views.custom_login, name='login'),
    path('register/', users_views.register, name='register'),
    #path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    #path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('logout/', users_views.signout, name='logout'),
    path('profile/', users_views.profile_fun, name='profile'),
    path('updateprofile/', users_views.update_profile, name='updateprofile'),
    path('single/<int:userid>/<int:orderid>/', users_views.single, name='single'),
]

urlpatterns += [

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)