from decimal import Decimal
from unittest.mock import Mock, patch

import requests
from django.conf import settings
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, override_settings
from django.urls import reverse

from products.models import Brand, Category, Product


@override_settings(EXTERNAL_API_BASE_URL="https://api.example.com")
class ProductViewsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Configuração executada uma vez para toda a classe de testes.
        """
        cls.user = User.objects.create_user(username="testuser", password="password123")
        cls.product_manager_group = Group.objects.create(name="Product Managers")
        content_type = ContentType.objects.get_for_model(Product)
        permissions = Permission.objects.filter(content_type=content_type)
        cls.product_manager_group.permissions.set(permissions)
        cls.user.groups.add(cls.product_manager_group)

        cls.brand = Brand.objects.create(name="Marca Teste")
        cls.category = Category.objects.create(name="Categoria Teste")
        cls.product = Product.objects.create(
            title="Notebook Teste",
            brand=cls.brand,
            category=cls.category,
            quantity=10,
            selling_price=Decimal("5000.00"),
            serie_number="NT123",
        )

    def setUp(self):
        """
        Configuração executada antes de cada teste.
        """
        self.client.login(username="testuser", password="password123")

    def test_product_list_view_loads_correctly(self):
        """Testa se a página de listagem de produtos carrega para um usuário autorizado."""
        response = self.client.get(reverse("product_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "product_list.html")
        self.assertContains(response, self.product.title)

    def test_product_list_view_search(self):
        """Testa a funcionalidade de busca na listagem."""
        response = self.client.get(reverse("product_list"), {"q": "Notebook"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Notebook Teste")

        response_no_result = self.client.get(reverse("product_list"), {"q": "Inexistente"})
        self.assertEqual(response_no_result.status_code, 200)
        self.assertNotContains(response_no_result, "Notebook Teste")

    @patch("products.views.requests.get")
    def test_product_list_view_with_api_products(self, mock_requests_get):
        """Testa se a listagem inclui produtos da API quando um token existe."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": 101, "title": "Produto da API"}]
        mock_requests_get.return_value = mock_response

        session = self.client.session
        session["api_jwt_token"] = "fake-token"
        session.save()

        response = self.client.get(reverse("product_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Produto da API")

    def test_product_detail_view_local_product(self):
        """Testa a exibição de detalhes de um produto local."""
        url = reverse("product_detail", kwargs={"pk": self.product.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "product_detail.html")
        self.assertContains(response, self.product.title)

    @patch("products.views.requests.get")
    def test_product_detail_view_api_product(self, mock_requests_get):
        """Testa a exibição de detalhes de um produto da API."""

        api_product_data = {
            "id": 101,
            "title": "Detalhe da API",
            "selling_price": "1250.75",
            "quantity": 15,
            "description": "Descrição do produto vinda da API.",
            "brand": {"name": "Marca Externa"},
            "category": {"name": "Categoria Externa"},
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = api_product_data
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response

        url = reverse("product_detail_api", kwargs={"external_id": 101})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "product_detail.html")
        self.assertContains(response, "Detalhe da API")
        self.assertContains(response, "Marca Externa")

    def test_product_create_view(self):
        """Testa a criação de um novo produto (GET para o formulário e POST para criar)."""
        response_get = self.client.get(reverse("product_create"))
        self.assertEqual(response_get.status_code, 200)
        self.assertTemplateUsed(response_get, "product_create.html")

        form_data = {
            "title": "Produto Novo",
            "brand": self.brand.pk,
            "category": self.category.pk,
            "selling_price": "123.45",
            "serie_number": "PN123",
            "quantity": 20,
        }
        response_post = self.client.post(reverse("product_create"), data=form_data)
        self.assertRedirects(response_post, reverse("product_list"))
        self.assertTrue(Product.objects.filter(title="Produto Novo").exists())

    def test_product_update_view(self):
        """Testa a atualização de um produto."""
        url = reverse("product_update", kwargs={"pk": self.product.pk})
        form_data = {
            "title": "Notebook Atualizado",
            "brand": self.brand.pk,
            "category": self.category.pk,
            "selling_price": "5500.00",
            "serie_number": "NT123",
            "quantity": 50,
        }
        response = self.client.post(url, data=form_data)
        self.assertRedirects(response, reverse("product_list"))

        self.product.refresh_from_db()
        self.assertEqual(self.product.title, "Notebook Atualizado")

    def test_product_delete_view(self):
        """Testa a deleção de um produto."""
        url = reverse("product_delete", kwargs={"pk": self.product.pk})
        response = self.client.post(url)
        self.assertRedirects(response, reverse("product_list"))
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())

    @patch("products.views.requests.get")
    def test_product_list_view_api_failure(self, mock_requests_get):
        """Testa a listagem quando a chamada à API externa falha."""
        mock_requests_get.side_effect = requests.exceptions.RequestException

        session = self.client.session
        session["api_jwt_token"] = "fake-token"
        session.save()

        response = self.client.get(reverse("product_list"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Produto da API")

    def test_product_detail_view_local_not_found(self):
        """Testa o redirect quando um produto local não existe."""
        url = reverse("product_detail", kwargs={"pk": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("product_list"))

    @patch("products.views.requests.get")
    def test_product_detail_view_api_not_found_404(self, mock_requests_get):
        """Testa o redirect quando a API retorna um 404."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_requests_get.return_value = mock_response

        url = reverse("product_detail_api", kwargs={"external_id": 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("product_list"))

    @patch("products.views.requests.get")
    def test_product_detail_view_api_photo_url_processing(self, mock_requests_get):
        """Testa a lógica de formatação de URL de foto da API."""

        base_api_data = {
            "id": 101,
            "title": "Produto com Foto",
            "selling_price": "1250.75",
            "quantity": 15,
            "description": "Descrição vinda da API.",
            "brand": {"name": "Marca Externa"},
            "category": {"name": "Categoria Externa"},
        }

        api_data_1 = base_api_data.copy()
        api_data_1["photo"] = "images/foto.jpg"

        mock_response = Mock(status_code=200)
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = api_data_1
        mock_requests_get.return_value = mock_response

        url = reverse("product_detail_api", kwargs={"external_id": 101})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        expected_photo_url = f"{settings.EXTERNAL_API_BASE_URL}/media/images/foto.jpg"
        self.assertContains(response, expected_photo_url)

        api_data_2 = base_api_data.copy()
        api_data_2["id"] = 102
        api_data_2["photo"] = "/media/images/foto2.jpg"

        mock_response.json.return_value = api_data_2
        url_2 = reverse("product_detail_api", kwargs={"external_id": 102})
        response_2 = self.client.get(url_2)

        self.assertEqual(response_2.status_code, 200)
        expected_photo_url_2 = f"{settings.EXTERNAL_API_BASE_URL}/media/images/foto2.jpg"
        self.assertContains(response_2, expected_photo_url_2)

    @patch("products.views.requests.get")
    def test_product_detail_view_api_general_failure(self, mock_requests_get):
        """Testa o redirect quando ocorre uma falha geral na API."""
        mock_requests_get.side_effect = requests.exceptions.Timeout

        url = reverse("product_detail_api", kwargs={"external_id": 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("product_list"))
