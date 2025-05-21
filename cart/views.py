from django.views import View
from django.shortcuts import render, redirect
from .cart import Cart
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect


class CartListView(View):
    def get(self, request):
        cart = Cart(request)
        return render(request, 'cart_list.html', {
            'cart_items': cart.items(),
            'total': cart.total(),
        })


class AddToCartView(View):
    def post(self, request, product_id):
        cart = Cart(request)
        quantity = int(request.POST.get('quantity', 1))
        cart.add(product_id, quantity)
        return redirect('home')


class RemoveFromCartView(View):
    def post(self, request, product_id):
        cart = Cart(request)
        cart.remove(product_id)
        return redirect('cart_list')


@method_decorator(csrf_protect, name='dispatch')
class UpdateCartItemView(View):
    def post(self, request, product_id):
        quantity = int(request.POST.get('quantity', 1))
        cart = Cart(request)
        if quantity > 0:
            cart.update(product_id, quantity)
        else:
            cart.remove(product_id)
        return redirect('cart_list')