from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from .forms import OrderForm
from .models import Order
from products.models import Product
from django.conf import settings
import urllib.parse
from cart.cart import Cart


class FinalizeOrderView(FormView):
    template_name = 'finalize_order.html'
    form_class = OrderForm
    success_url = reverse_lazy('cart_list')

    def get_cart(self):
        return Cart(self.request)

    def form_valid(self, form):
        cart = self.get_cart()
        products_in_cart = Product.objects.filter(id__in=cart.cart.keys())

        order = form.save()

        product_lines = []
        for product in products_in_cart:
            quantity = cart.cart.get(str(product.id), 0)
            product_lines.append(f"{product.title} (x{quantity})")

        products_text = "\n".join(product_lines) if product_lines else "Nenhum produto no carrinho."

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
        context['cart_items'] = self.get_cart().items()
        context['total'] = self.get_cart().total()
        return context
