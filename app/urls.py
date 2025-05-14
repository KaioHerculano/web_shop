from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('brands.urls')),
    path('', include('categories.urls')),
    path('', include('cart.urls')),
    path('', include('products.urls')),
    path('', views.HomeView.as_view(), name='home'),
]
