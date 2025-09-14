from django.conf import settings
from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse

from brands.models import Brand


class BrandViewsTest(TestCase):

    # O método setUp é executado ANTES de cada teste
    def setUp(self):
        """Prepara o ambiente para os testes das views."""
        # Usuário comum, sem permissões
        self.test_user = User.objects.create_user(username="testuser", password="password123")

        # Usuário com todas as permissões do app 'brands'
        self.perm_user = User.objects.create_user(username="permuser", password="password123")
        permissions = Permission.objects.filter(content_type__app_label="brands")
        self.perm_user.user_permissions.set(permissions)

        # URLs que serão usadas com frequência
        self.list_url = reverse("brand_list")
        self.create_url = reverse("brand_create")

        # Uma instância de Brand para testes de update, detail e delete
        self.brand = Brand.objects.create(name="Brand Exemplo")

    def test_brand_list_view_authenticated(self):
        self.client.login(username="permuser", password="password123")
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        # self.assertContains checa o status code e se o texto está no conteúdo
        self.assertContains(response, "Brand Exemplo")

    def test_brand_list_view_unauthenticated(self):
        response = self.client.get(self.list_url)

        # --- ALTERAÇÃO AQUI ---
        # Em vez de um valor fixo, usamos a configuração do projeto.
        expected_url = f"{settings.LOGIN_URL}?next={self.list_url}"
        self.assertRedirects(response, expected_url)

    def test_brand_list_search(self):
        self.client.login(username="permuser", password="password123")
        Brand.objects.create(name="Item a ser achado")

        response = self.client.get(self.list_url + "?q=achado")

        self.assertContains(response, "Item a ser achado")
        self.assertNotContains(
            response, "Brand Exemplo"
        )  # Não deve aparecer no resultado da busca

    def test_brand_create_view_post(self):
        self.client.login(username="permuser", password="password123")

        form_data = {"name": "Marca Criada", "description": "Criada via teste"}
        response = self.client.post(self.create_url, data=form_data)

        self.assertRedirects(response, self.list_url)
        self.assertTrue(Brand.objects.filter(name="Marca Criada").exists())

    def test_brand_create_view_no_permission(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_brand_delete_view(self):
        self.client.login(username="permuser", password="password123")

        # A brand a ser deletada foi criada no setUp
        delete_url = reverse("brand_delete", kwargs={"pk": self.brand.pk})
        response = self.client.post(delete_url)

        self.assertRedirects(response, self.list_url)
        self.assertFalse(Brand.objects.filter(pk=self.brand.pk).exists())
