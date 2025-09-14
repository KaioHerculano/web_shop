from decimal import Decimal

from django.test import RequestFactory, TestCase

from brands.models import Brand
from cart.cart import Cart
from categories.models import Category
from products.models import Product


class CartLogicTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        brand = Brand.objects.create(name="Marca Local")
        category = Category.objects.create(name="Categoria de Teste")
        cls.local_product = Product.objects.create(
            title="Produto Local", brand=brand, category=category, selling_price=Decimal("150.00")
        )
        cls.api_product_data = {
            "id": 123,
            "title": "Produto da API",
            "selling_price": 99.99,
        }

    def setUp(self):
        self.request = RequestFactory().get("/")
        self.request.session = self.client.session

    def test_add_local_product(self):
        cart = Cart(self.request)
        cart.add(product_id=self.local_product.id, quantity=2)
        expected_key = f"local-{self.local_product.id}"
        self.assertIn(expected_key, cart.cart)
        self.assertEqual(cart.cart[expected_key]["quantity"], 2)

    def test_add_api_product(self):
        cart = Cart(self.request)
        cart.add_api_product(product_data=self.api_product_data, quantity=1)
        expected_key = f"api-{self.api_product_data['id']}"
        self.assertIn(expected_key, cart.cart)
        self.assertEqual(cart.cart[expected_key]["quantity"], 1)

    def test_update_and_remove_products(self):
        cart = Cart(self.request)
        cart.add(product_id=self.local_product.id, quantity=1)
        # Remove
        cart.remove(product_id=self.local_product.id, product_type="local")
        self.assertNotIn(f"local-{self.local_product.id}", cart.cart)

    def test_items_and_total_calculation_with_mixed_cart(self):
        cart = Cart(self.request)
        cart.add(product_id=self.local_product.id, quantity=2)
        cart.add_api_product(product_data=self.api_product_data, quantity=1)
        self.assertEqual(cart.total(), Decimal("399.99"))

    def test_cart_initialization_with_empty_session(self):
        cart = Cart(self.request)
        self.assertEqual(cart.cart, {})

    def test_items_method_handles_malformed_session_data(self):
        session = self.client.session
        session["cart"] = {
            f"local-{self.local_product.id}": {"quantity": 1, "type": "local"},
            "dado_invalido": "isto nao e um dicionario",
        }
        session.save()
        cart = Cart(self.request)
        self.assertEqual(len(cart.items()), 0)

    def test_total_and_items_on_empty_cart(self):
        cart = Cart(self.request)
        self.assertEqual(cart.total(), Decimal("0"))
        self.assertEqual(cart.items(), [])

    def test_clear_cart(self):
        cart = Cart(self.request)
        cart.add(product_id=self.local_product.id, quantity=5)
        cart.clear()
        self.assertEqual(cart.cart, {})
