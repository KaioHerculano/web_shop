import urllib.parse

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

    def test_finalize_order_get_request_loads_page(self):
        """Testa se uma requisição GET para a view carrega a página corretamente."""
        url = reverse("finalize_order")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "finalize_order.html")

        # Verifica se o contexto foi populado corretamente
        self.assertIn("cart_items", response.context)
        self.assertIn("total", response.context)
        self.assertIsNotNone(response.context["form"])

    def test_finalize_order_with_api_product(self):
        """Testa a finalização de um pedido contendo um produto da API."""
        # Adiciona um produto da API ao carrinho
        session = self.client.session
        session["cart"] = {
            "api-123": {
                "quantity": 3,
                "type": "api",
                "title": "Produto da API Teste",
                "price": 50.0,
            }
        }
        session.save()

        url = reverse("finalize_order")
        form_data = {
            "customer_name": "Cliente API",
            "address": "Rua API, 456",
            "phone": "11888888888",
            "payment_method": "credit_card",
        }

        response = self.client.post(url, data=form_data)

        self.assertEqual(response.status_code, 302)
        self.assertIn("https://wa.me/", response.url)

        # Decodifica a URL para verificar se o produto da API está na mensagem
        redirect_url = response.url
        parsed_url = urllib.parse.urlparse(redirect_url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        message = query_params.get("text", [""])[0]

        self.assertIn("Produto da API Teste (x3)", message)

        # Verifica se o pedido foi criado
        self.assertTrue(Order.objects.filter(customer_name="Cliente API").exists())
