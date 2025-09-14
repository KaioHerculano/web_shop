from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import views

urlpatterns = [
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("admin/", admin.site.urls),
    path("", include("brands.urls")),
    path("", include("categories.urls")),
    path("", include("cart.urls")),
    path("", include("products.urls")),
    path("", include("orders.urls")),
    path("", views.HomeView.as_view(), name="home"),
]
