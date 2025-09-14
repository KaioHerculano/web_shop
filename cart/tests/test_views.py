from unittest.mock import Mock, patch

import requests
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
            title="Produto Local View", brand=brand, category=category, selling_price=100.00
        )
        cls.api_product_data = {"id": 456, "title": "Produto API View", "selling_price": 50.00}

        cls.add_local_url = reverse("add_to_cart", args=[cls.local_product.id])
        cls.add_api_url = reverse("add_api_product_to_cart", args=[cls.api_product_data["id"]])
        cls.list_url = reverse("cart_list")

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
        # 1. Configuramos o mock para simular a resposta da API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.api_product_data
        mock_requests_get.return_value = mock_response

        # 2. Chamamos a view
        response = self.client.post(self.add_api_url, {"quantity": 1})

        # 3. Verificamos os resultados
        self.assertEqual(response.status_code, 302)
        api_product_key = f"api-{self.api_product_data['id']}"
        self.assertEqual(self.client.session["cart"][api_product_key]["quantity"], 1)

        # 4. Verificamos se a chamada de rede foi feita como esperado
        expected_api_url = (
            f"http://127.0.0.1:5000/api/v1/public/products/1/{self.api_product_data['id']}/"
        )
        mock_requests_get.assert_called_once_with(expected_api_url, timeout=5)

    @patch("cart.views.requests.get")
    def test_add_api_product_view_failure(self, mock_requests_get):
        """Testa a view que adiciona produto da API, simulando uma falha de rede."""
        # Configuramos o mock para simular um erro
        mock_requests_get.side_effect = requests.exceptions.RequestException("API fora do ar")

        response = self.client.post(self.add_api_url, {"quantity": 1})

        self.assertEqual(response.status_code, 302)  # Redireciona de volta
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
