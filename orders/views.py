import urllib.parse

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from cart.cart import Cart
from products.models import Product

from .forms import OrderForm


class FinalizeOrderView(FormView):
    template_name = "finalize_order.html"
    form_class = OrderForm
    success_url = reverse_lazy("cart_list")

    def get_cart(self):
        return Cart(self.request)

    def form_valid(self, form):
        cart = self.get_cart()
        # Só ids locais para buscar no banco
        local_ids = [key.split("-", 1)[1] for key in cart.cart.keys() if key.startswith("local-")]
        products_in_cart = Product.objects.filter(id__in=local_ids)

        order = form.save()

        product_lines = []
        # Produtos locais
        for product in products_in_cart:
            key = f"local-{product.id}"
            quantity = cart.cart.get(key, {}).get("quantity", 0)
            product_lines.append(f"{product.title} (x{quantity})")
        # Produtos da API
        for key, data in cart.cart.items():
            if isinstance(data, dict) and data.get("type") == "api":
                title = data.get("title", "Produto da API")
                quantity = data.get("quantity", 0)
                product_lines.append(f"{title} (x{quantity})")

        products_text = (
            "\n".join(product_lines) if product_lines else "Nenhum produto no carrinho."
        )

        message = (
            f"Novo pedido!\n"
            f"Cliente: {order.customer_name}\n"
            f"Endereço: {order.address}\n"
            f"Telefone: {order.phone}\n"
            f"Pagamento: {order.get_payment_method_display()}\n"
            f"Produtos:\n{products_text}\n"
            f"Pedido ID: {order.id}"
        )
        encoded_message = urllib.parse.quote(message)
        merchant_phone = settings.MERCHANT_WHATSAPP_NUMBER
        whatsapp_url = f"https://wa.me/{merchant_phone}?text={encoded_message}"

        cart.clear()

        return redirect(whatsapp_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cart_items"] = self.get_cart().items()
        context["total"] = self.get_cart().total()
        return context
