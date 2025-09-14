# orders/tests/test_views.py
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from orders.models import Order
from products.models import Brand, Category, Product


@override_settings(MERCHANT_WHATSAPP_NUMBER="5511999999999")
class FinalizeOrderViewTest(TestCase):
    def setUp(self):
        self.client = Client()

        # Criar brand obrigatório para Product
        self.brand = Brand.objects.create(name="Marca Teste")
        # Criar category obrigatório para Product
        self.category = Category.objects.create(name="Categoria Teste")

        self.product = Product.objects.create(
            title="Produto Teste",
            selling_price=10.0,
            brand=self.brand,
            category=self.category,
        )

        # Inicializa o carrinho na sessão
        session = self.client.session
        session["cart"] = {f"local-{self.product.id}": {"quantity": 2, "type": "local"}}
        session.save()

    def test_finalize_order_redirects_to_whatsapp(self):
        url = reverse("finalize_order")
        form_data = {
            "customer_name": "Kaio Herculano",
            "address": "Rua Exemplo, 123",
            "phone": "11999999999",
            "payment_method": "pix",
        }

        response = self.client.post(url, data=form_data)

        # Verifica o redirect para o WhatsApp
        self.assertEqual(response.status_code, 302)
        self.assertIn("https://wa.me/", response.url)

        # Pedido criado corretamente
        order = Order.objects.first()
        self.assertIsNotNone(order)
        self.assertEqual(order.customer_name, "Kaio Herculano")

        session = self.client.session
        session.modified = True
        session = self.client.session
        self.assertEqual(session.get("cart", {}), {})

    def test_finalize_order_with_empty_cart(self):
        # Limpa o carrinho
        session = self.client.session
        session["cart"] = {}
        session.save()

        url = reverse("finalize_order")
        form_data = {
            "customer_name": "Kaio Herculano",
            "address": "Rua Exemplo, 123",
            "phone": "11999999999",
            "payment_method": "pix",
        }
        response = self.client.post(url, data=form_data)

        self.assertEqual(response.status_code, 302)
        self.assertIn("https://wa.me/", response.url)

        # Pedido ainda é criado mesmo sem produtos
        order = Order.objects.first()
        self.assertIsNotNone(order)
