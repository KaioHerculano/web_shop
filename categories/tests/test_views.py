from django.conf import settings
from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse

from categories.models import Category


class CategoryViewsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Cria usuários, permissões e uma categoria para serem usados nos testes."""
        # Usuário comum, sem permissões
        cls.user = User.objects.create_user(username="testuser", password="password123")

        # Usuário com todas as permissões do app 'categories'
        cls.perm_user = User.objects.create_user(username="permuser", password="password123")
        permissions = Permission.objects.filter(content_type__app_label="categories")
        cls.perm_user.user_permissions.set(permissions)

        # Uma categoria de exemplo
        cls.category = Category.objects.create(name="Tecnologia")

        # URLs
        cls.list_url = reverse("category_list")
        cls.create_url = reverse("category_create")
        cls.detail_url = reverse("category_detail", kwargs={"pk": cls.category.pk})
        cls.update_url = reverse("category_update", kwargs={"pk": cls.category.pk})
        cls.delete_url = reverse("category_delete", kwargs={"pk": cls.category.pk})

    def test_views_redirect_if_not_logged_in(self):
        """Testa se todas as views redirecionam para a tela de login se o usuário não estiver logado."""
        urls = [self.list_url, self.create_url, self.detail_url, self.update_url, self.delete_url]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                expected_redirect_url = f"{settings.LOGIN_URL}?next={url}"
                self.assertRedirects(response, expected_redirect_url)

    def test_views_fail_if_user_lacks_permission(self):
        """Testa se as views retornam 403 Forbidden se o usuário não tiver a permissão necessária."""
        self.client.login(username="testuser", password="password123")
        urls_to_check = {
            self.list_url: 403,
            self.create_url: 403,
            self.detail_url: 403,
            self.update_url: 403,
            self.delete_url: 403,
        }
        for url, status_code in urls_to_check.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_category_list_view_search(self):
        """Testa a funcionalidade de busca da ListView."""
        self.client.login(username="permuser", password="password123")
        Category.objects.create(name="Decoração")  # Categoria extra

        response = self.client.get(self.list_url + "?q=Tecno")

        self.assertContains(response, "Tecnologia")
        self.assertNotContains(response, "Decoração")

    def test_category_create_view_post(self):
        """Testa a criação de uma nova categoria via POST."""
        self.client.login(username="permuser", password="password123")
        form_data = {"name": "Esportes", "description": "Artigos esportivos"}

        response = self.client.post(self.create_url, data=form_data)

        self.assertRedirects(response, self.list_url)
        self.assertTrue(Category.objects.filter(name="Esportes").exists())

    def test_category_update_view_post(self):
        """Testa a atualização de uma categoria via POST."""
        self.client.login(username="permuser", password="password123")

        # Se self.category.description for None, usamos '' no lugar.
        form_data = {"name": "Tecnologia Avançada", "description": self.category.description or ""}

        response = self.client.post(self.update_url, data=form_data)
        self.assertRedirects(response, self.list_url)

        # Atualiza o objeto do banco de dados para verificar a mudança
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Tecnologia Avançada")

    def test_category_delete_view_post(self):
        """Testa a exclusão de uma categoria via POST."""
        self.client.login(username="permuser", password="password123")

        response = self.client.post(self.delete_url)

        self.assertRedirects(response, self.list_url)
        self.assertFalse(Category.objects.filter(pk=self.category.pk).exists())
