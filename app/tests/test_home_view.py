from decimal import Decimal
from unittest.mock import MagicMock, patch

import requests
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase, override_settings

from app.views import HomeView, ProductData
from products.models import Brand, Category, Product

# Dados mocados da API para usar nos testes
MOCKED_API_PRODUCTS = [
    {
        "id": 101,
        "title": "API Produto A",
        "selling_price": "5.50",
        "discount_price": "4.99",
        "quantity": 10,
        "photo": "/media/fotoA.jpg",
    },
    {
        "id": 102,
        "title": "API Produto B",
        "price": "12.00",
        "quantity": 5,
        "photo_url": "http://example.com/fotoB.jpg",
    },
    {"id": 103, "title": "API Produto C (Sem estoque)", "selling_price": "20.00", "quantity": 0},
    {"id": 104, "title": "API Produto D", "selling_price": "9.00", "quantity": 1},
]


class HomeViewTest(TestCase):
    def setUp(self):
        """
        Configura o ambiente de teste com dados variados para cobrir diferentes cenários,
        incluindo múltiplas categorias para testar a funcionalidade de filtro.
        """
        self.factory = RequestFactory()
        self.user = AnonymousUser()

        # --- Dados base ---
        self.brand1 = Brand.objects.create(name="Marca Teste")

        # 1. Criamos DUAS categorias distintas para testar o filtro
        self.cat_frutas = Category.objects.create(name="Frutas")
        self.cat_laticinios = Category.objects.create(name="Laticínios")

        # 2. Criamos um produto para CADA categoria com nomes de variáveis mais claros

        # Produto barato, sem desconto, na categoria Frutas
        self.prod_fruta = Product.objects.create(
            title="Maçã Local",
            selling_price=Decimal("2.50"),
            quantity=20,
            category=self.cat_frutas,
            brand=self.brand1,
            serie_number="FRT001",
        )

        # Produto mais caro, com desconto, na categoria Laticínios
        self.prod_laticinio = Product.objects.create(
            title="Queijo Minas",
            selling_price=Decimal("25.00"),
            discount_price=Decimal("22.50"),
            quantity=10,
            category=self.cat_laticinios,
            brand=self.brand1,
            serie_number="LAT001",
        )

    def _setup_request_with_messages(self, request):
        """Adiciona suporte a mensagens em um request de factory."""
        setattr(request, "session", "session")
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        return request

    @patch("app.views.requests.get")
    def test_get_context_data_sucesso(self, mock_get):
        """
        Testa o caminho feliz: dados locais e da API são carregados e processados.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCKED_API_PRODUCTS
        mock_get.return_value = mock_response

        request = self.factory.get("/")
        request.user = self.user
        request = self._setup_request_with_messages(request)

        view = HomeView()
        view.setup(request)
        context = view.get_context_data()

        self.assertEqual(len(context["cheapest_products"]), 3)
        self.assertEqual(context["cheapest_products"][0].title, "Maçã Local")
        self.assertEqual(context["cheapest_products"][1].title, "API Produto A")
        self.assertEqual(context["cheapest_products"][2].title, "API Produto D")

        self.assertEqual(len(context["products"]), 2)
        titles = {p.title for p in context["products"]}
        # CORREÇÃO: Verifica pelo nome correto do produto definido no setUp
        self.assertIn("Queijo Minas", titles)
        self.assertIn("API Produto B", titles)

    @patch("app.views.requests.get")
    def test_get_context_data_com_filtros_de_busca(self, mock_get):
        """
        Testa a aplicação do filtro de busca por termo.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCKED_API_PRODUCTS
        mock_get.return_value = mock_response

        request = self.factory.get("/", {"q": "API"})
        request.user = self.user
        request = self._setup_request_with_messages(request)

        view = HomeView()
        view.setup(request)
        context = view.get_context_data()

        all_products = context["cheapest_products"] + context["products"]
        self.assertTrue(all(p.is_api for p in all_products))
        self.assertEqual(len(all_products), 3)

    @patch("app.views.requests.get")
    def test_get_context_data_falha_api(self, mock_get):
        """
        Testa o tratamento de exceção quando a API falha.
        """
        mock_get.side_effect = requests.exceptions.Timeout("API timed out")

        request = self.factory.get("/")
        request.user = self.user
        request = self._setup_request_with_messages(request)

        view = HomeView()
        view.setup(request)
        context = view.get_context_data()

        self.assertEqual(len(context["cheapest_products"]), 1)
        self.assertEqual(context["cheapest_products"][0].title, "Maçã Local")
        self.assertEqual(len(context["products"]), 1)
        # CORREÇÃO: Verifica pelo nome correto do produto definido no setUp
        self.assertEqual(context["products"][0].title, "Queijo Minas")

        messages = list(request._messages)
        self.assertEqual(len(messages), 1)

    def test_get_actual_price_for_sort(self):
        """
        Testa o método estático de ordenação de preços de forma isolada.
        """
        p1 = ProductData(
            id=1, title="P1", selling_price=Decimal("10"), discount_price=Decimal("8")
        )
        self.assertEqual(HomeView.get_actual_price_for_sort(p1), Decimal("8"))

        p2 = ProductData(id=2, title="P2", selling_price=Decimal("10"), discount_price=None)
        self.assertEqual(HomeView.get_actual_price_for_sort(p2), Decimal("10"))

        p3 = ProductData(id=3, title="P3", selling_price="inválido", discount_price=None)
        self.assertEqual(HomeView.get_actual_price_for_sort(p3), Decimal("0.00"))

        p4 = ProductData(id=4, title="P4", selling_price=None, discount_price=None)
        self.assertEqual(HomeView.get_actual_price_for_sort(p4), Decimal("0.00"))

    @override_settings(EXTERNAL_API_BASE_URL="http://test-api.com")
    def test_transform_api_product_photo_url_logic(self):
        """
        Testa a lógica de transformação de URL de foto.
        """
        view = HomeView()
        api_base_url = settings.EXTERNAL_API_BASE_URL

        product_item = {
            "id": 201,
            "title": "Produto com foto simples",
            "selling_price": "50.00",
            "quantity": 1,
            "photo": "foto_simples.jpg",
        }

        product_data = view._transform_api_product(product_item, 1, api_base_url)

        expected_url = "http://test-api.com/media/foto_simples.jpg"
        self.assertEqual(product_data.photo, expected_url)

    @patch("app.views.requests.get")
    def test_get_context_data_filters_by_category(self, mock_get):
        """
        Verifica se a view filtra corretamente os produtos locais por categoria.
        """
        mock_get.return_value.json.return_value = []

        request = self.factory.get("/", {"category": "Frutas"})
        request.user = self.user
        request = self._setup_request_with_messages(request)

        view = HomeView()
        view.setup(request)
        context = view.get_context_data()

        returned_products = context["cheapest_products"] + context["products"]
        product_titles = {p.title for p in returned_products}

        # CORREÇÃO: Usa o nome exato do produto e da categoria para o teste
        self.assertIn("Maçã Local", product_titles)
        self.assertNotIn("Queijo Minas", product_titles)
        self.assertEqual(len(returned_products), 1)
