from django.urls import path

from . import views

urlpatterns = [
    path("cart/list/", views.CartListView.as_view(), name="cart_list"),
    path("add/<int:product_id>/", views.AddToCartView.as_view(), name="add_to_cart"),
    path("remove/<str:product_id>/", views.RemoveFromCartView.as_view(), name="remove_from_cart"),
    path(
        "cart/update/<str:product_id>/",
        views.UpdateCartItemView.as_view(),
        name="update_cart_item",
    ),
    path(
        "add-api-to-cart/<str:product_id>/",
        views.AddApiProductToCartView.as_view(),
        name="add_api_product_to_cart",
    ),
]
