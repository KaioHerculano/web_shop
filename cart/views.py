from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from .cart import Cart
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from products import models as product_models
import requests
from django.contrib import messages


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
        product = get_object_or_404(product_models.Product, pk=product_id)
        cart.add(product_id=product.id, quantity=quantity)
        messages.success(request, f"Produto '{product.title}' adicionado ao carrinho.")
        return redirect('home')


class AddApiProductToCartView(View):
    def post(self, request, product_id):
        token = request.session.get('api_jwt_token')
        if not token:
            messages.error(request, "Você precisa estar autenticado na API para adicionar este produto.")
            return redirect('home')
        
        api_url = f'http://127.0.0.1:5000/api/v1/products/{product_id}/'  # corrigido 'http:'
        headers = {'Authorization': f'Bearer {token}'}

        try:
            response = requests.get(api_url, headers=headers, timeout=5)
            response.raise_for_status()
            product_data = response.json()
        except Exception as e:
            messages.error(request, f"Erro ao buscar produto na API: {e}")
            return redirect('home')

        product_info = {
            'id': product_data['id'],
            'title': product_data.get('title', 'Produto da API'),
            'price': product_data.get('selling_price', 0),
        }

        quantity = int(request.POST.get('quantity', 1))
        cart = Cart(request)
        cart.add_api_product(product_info, quantity)

        messages.success(request, f"Produto '{product_info['title']}' adicionado ao carrinho.")
        return redirect('cart_list')


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
