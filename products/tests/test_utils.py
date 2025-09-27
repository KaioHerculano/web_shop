from unittest.mock import Mock, patch

import requests
from django.conf import settings
from django.test import TestCase, override_settings

from products.utils import fetch_external_products


@override_settings(EXTERNAL_API_BASE_URL="https://api.example.com")
class FetchExternalProductsTest(TestCase):

    @patch("products.utils.requests.get")
    def test_fetch_external_products_success(self, mock_requests_get):
        """
        Testa o caso de sucesso, onde a API retorna dados de produtos.
        """
        # Arrange: Prepara o mock para simular uma resposta de sucesso da API
        expected_data = [{"id": 1, "title": "Produto Externo 1"}]

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = expected_data
        # A função raise_for_status() não faz nada em caso de sucesso (status 200)
        mock_response.raise_for_status.return_value = None

        mock_requests_get.return_value = mock_response

        # Act: Chama a função que queremos testar
        result = fetch_external_products()

        # Assert: Verifica se o resultado está correto
        self.assertEqual(result, expected_data)

        # Verifica se requests.get foi chamado com a URL correta
        expected_url = f"{settings.EXTERNAL_API_BASE_URL}/api/v1/products/"
        mock_requests_get.assert_called_once_with(expected_url, timeout=5)

    @patch("products.utils.requests.get")
    def test_fetch_external_products_failure(self, mock_requests_get):
        """
        Testa o caso de falha, onde a API não responde ou retorna um erro.
        """
        # Arrange: Configura o mock para simular uma exceção de rede
        mock_requests_get.side_effect = requests.exceptions.RequestException("API indisponível")

        # Act: Chama a função
        result = fetch_external_products()

        # Assert: Verifica se a função retorna uma lista vazia em caso de erro
        self.assertEqual(result, [])
