from decimal import Decimal
from unittest.mock import Mock, patch

import requests
from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from brands.models import Brand
from categories.models import Category
from products.models import Product


class CartViewsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        brand = Brand.objects.create(name="Marca de Teste")
        category = Category.objects.create(name="Categoria de Teste")

        cls.local_product = Product.objects.create(
            title="Produto Local View",
            brand=brand,
            category=category,
            selling_price=Decimal("100.00"),
        )
        cls.api_product_data = {"id": 456, "title": "Produto API View", "selling_price": 50.00}

        cls.add_local_url = reverse("add_to_cart", args=[cls.local_product.id])
        cls.add_api_url = reverse("add_api_product_to_cart", args=[cls.api_product_data["id"]])
        cls.list_url = reverse("cart_list")
        cls.remove_local_url = reverse("remove_from_cart", args=[cls.local_product.id])
        cls.update_local_url = reverse("update_cart_item", args=[cls.local_product.id])

    def test_add_local_product_view(self):
        """Testa a view que adiciona um produto local."""
        response = self.client.post(self.add_local_url, {"quantity": 3})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            self.client.session["cart"][f"local-{self.local_product.id}"]["quantity"], 3
        )

    @patch("cart.views.requests.get")
    def test_add_api_product_view_success(self, mock_requests_get):
        """Testa a view que adiciona produto da API, simulando uma resposta de sucesso."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.api_product_data
        mock_requests_get.return_value = mock_response

        response = self.client.post(self.add_api_url, {"quantity": 1})

        self.assertEqual(response.status_code, 302)
        api_product_key = f"api-{self.api_product_data['id']}"
        self.assertEqual(self.client.session["cart"][api_product_key]["quantity"], 1)

        expected_api_url = f"{settings.EXTERNAL_API_BASE_URL}/api/v1/public/products/1/{self.api_product_data['id']}/"
        mock_requests_get.assert_called_once_with(expected_api_url, timeout=5)

    @patch("cart.views.requests.get")
    def test_add_api_product_view_failure(self, mock_requests_get):
        """Testa a view que adiciona produto da API, simulando uma falha de rede."""
        mock_requests_get.side_effect = requests.exceptions.RequestException("API fora do ar")
        response = self.client.post(self.add_api_url, {"quantity": 1})
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(f"api-{self.api_product_data['id']}", self.client.session.get("cart", {}))

    def test_cart_list_view_with_mixed_items(self):
        """Testa se a view de listagem exibe produtos locais e da API."""
        session = self.client.session
        session["cart"] = {
            f"local-{self.local_product.id}": {"quantity": 2, "type": "local"},
            f"api-{self.api_product_data['id']}": {
                "quantity": 1,
                "type": "api",
                "title": "Produto API View",
                "price": 50.00,
            },
        }
        session.save()

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Produto Local View")
        self.assertContains(response, "Produto API View")

    def test_remove_from_cart_view(self):
        """Testa a remoção de um item pela RemoveFromCartView."""
        self.client.post(self.add_local_url)
        response = self.client.post(self.remove_local_url, {"type": "local"})
        self.assertRedirects(response, self.list_url)
        self.assertEqual(len(self.client.session.get("cart", {})), 0)

    def test_update_cart_item_view_updates_quantity(self):
        """Testa a atualização da quantidade pela UpdateCartItemView."""
        self.client.post(self.add_local_url, {"quantity": 1})
        response = self.client.post(self.update_local_url, {"quantity": 5, "type": "local"})
        self.assertRedirects(response, self.list_url)
        key = f"local-{self.local_product.id}"
        self.assertEqual(self.client.session["cart"][key]["quantity"], 5)

    @patch("cart.views.requests.get")
    def test_update_cart_item_view_removes_on_zero_quantity(self, mock_requests_get):
        """Testa a remoção via UpdateCartItemView com quantidade 0."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.api_product_data
        mock_requests_get.return_value = mock_response

        self.client.post(self.add_api_url)

        update_api_url = reverse("update_cart_item", args=[self.api_product_data["id"]])

        response = self.client.post(update_api_url, {"quantity": 0, "type": "api"})

        self.assertRedirects(response, self.list_url)
        self.assertEqual(len(self.client.session.get("cart", {})), 0)
