from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('admin/', admin.site.urls),

    path('', include('brands.urls')),
    path('', include('categories.urls')),
    path('', include('cart.urls')),
    path('', include('products.urls')),
    path('', include('orders.urls')),
    path('', views.HomeView.as_view(), name='home'),
]
