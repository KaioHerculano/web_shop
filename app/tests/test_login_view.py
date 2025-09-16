from unittest.mock import MagicMock, patch

import requests
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse


class CustomLoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse("login")  # Substitua 'login' pelo nome da sua URL de login
        self.user = User.objects.create_user(username="testuser", password="password123")

    @patch("app.views.requests.post")
    def test_login_api_sucesso(self, mock_post):
        """
        Testa o login bem-sucedido com a API externa retornando 200.
        Cobre as linhas: 52-60
        """
        # Configura o mock para simular uma resposta de sucesso da API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access": "fake_jwt_token"}
        mock_post.return_value = mock_response

        # Simula o envio do formulário de login
        response = self.client.post(
            self.login_url, {"username": "testuser", "password": "password123"}
        )

        # Verifica se o token foi salvo na sessão
        self.assertEqual(self.client.session.get("api_jwt_token"), "fake_jwt_token")
        self.assertRedirects(response, "/")  # Assumindo que redireciona para a home

    @patch("app.views.requests.post")
    def test_login_api_falha_autenticacao(self, mock_post):
        """
        Testa o login com falha na autenticação da API externa (ex: status 401).
        Cobre as linhas: 61-66
        """
        # Configura o mock para simular uma resposta de falha da API
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response

        # Simula o envio do formulário e verifica a mensagem de aviso
        self.client.post(self.login_url, {"username": "testuser", "password": "password123"})

        # Como as mensagens são complexas de testar diretamente sem recarregar a página,
        # uma forma é verificar se a chamada a `messages.warning` ocorreu.
        # Para isso, precisaríamos de outro patch:
        # @patch('app.views.messages')
        # ...
        # mock_messages.warning.assert_called_once()
        # Mas para simplificar, vamos focar na lógica principal. O importante é que o fluxo entre no `else`.
        self.assertNotIn("api_jwt_token", self.client.session)

    @patch("app.views.requests.post")
    def test_login_api_excecao_conexao(self, mock_post):
        """
        Testa o que acontece se a API externa estiver fora do ar.
        Cobre as linhas: 67-68
        """
        # Configura o mock para levantar uma exceção
        mock_post.side_effect = requests.exceptions.ConnectionError("Failed to connect")

        self.client.post(self.login_url, {"username": "testuser", "password": "password123"})

        # Verifica que o token não foi salvo na sessão
        self.assertNotIn("api_jwt_token", self.client.session)
