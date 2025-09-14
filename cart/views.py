import requests
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect

from products import models as product_models

from .cart import Cart


class CartListView(View):
    def get(self, request):
        cart = Cart(request)
        ids_puros = []
        for key in cart.cart.keys():
            if key.startswith("local-"):
                ids_puros.append(key.split("-", 1)[1])
        produtos = product_models.Product.objects.filter(id__in=ids_puros)
        return render(
            request,
            "cart_list.html",
            {
                "cart_items": cart.items(),
                "total": cart.total(),
                "produtos": produtos,
            },
        )


class AddToCartView(View):
    def post(self, request, product_id):
        cart = Cart(request)
        quantity = int(request.POST.get("quantity", 1))
        product = get_object_or_404(product_models.Product, pk=product_id)
        cart.add(product_id=product.id, quantity=quantity)
        messages.success(request, f"Produto '{product.title}' adicionado ao carrinho.")
        return redirect("home")


class AddApiProductToCartView(View):
    def post(self, request, product_id):
        api_url = f"http://127.0.0.1:5000/api/v1/public/products/1/{product_id}/"
        try:
            response = requests.get(api_url, timeout=5)
            response.raise_for_status()
            product_data = response.json()
        except Exception as e:
            messages.error(request, f"Erro ao buscar produto na API: {e}")
            return redirect(request.META.get("HTTP_REFERER", "home"))

        quantity = int(request.POST.get("quantity", 1))
        cart = Cart(request)
        cart.add_api_product(product_data=product_data, quantity=quantity)

        messages.success(
            request,
            f"Produto '{product_data.get('title', 'Produto da API')}' adicionado ao carrinho.",
        )
        return redirect(request.META.get("HTTP_REFERER", "home"))


class RemoveFromCartView(View):
    def post(self, request, product_id):
        product_type = request.POST.get("type")
        cart = Cart(request)
        cart.remove(product_id, product_type=product_type)
        return redirect("cart_list")


@method_decorator(csrf_protect, name="dispatch")
class UpdateCartItemView(View):
    def post(self, request, product_id):
        quantity = int(request.POST.get("quantity", 1))
        product_type = request.POST.get("type", "local")
        cart = Cart(request)
        if quantity > 0:
            cart.update(product_id, quantity, product_type=product_type)
        else:
            cart.remove(product_id, product_type="api")
        return redirect("cart_list")
