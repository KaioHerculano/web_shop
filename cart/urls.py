from django.urls import path
from . import views

urlpatterns = [
    path('cart/list/', views.CartListView.as_view(), name='cart_list'),
    path('add/<int:product_id>/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('remove/<int:product_id>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
]
