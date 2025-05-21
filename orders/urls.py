from django.urls import path
from . import views

urlpatterns = [
    path('finalizar-pedido/', views.FinalizeOrderView.as_view(), name='finalize_order'),
]
