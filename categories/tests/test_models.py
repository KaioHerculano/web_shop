from datetime import timedelta
from time import sleep

from django.test import TestCase

from categories.models import Category


class CategoryModelTest(TestCase):

    def test_category_creation(self):
        """Testa a criação de uma categoria e a representação __str__."""
        category = Category.objects.create(name="Eletrônicos")
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(str(category), "Eletrônicos")

    def test_category_ordering(self):
        """Testa se a ordenação padrão por nome está funcionando."""
        Category.objects.create(name="Roupas")
        Category.objects.create(name="Acessórios")
        Category.objects.create(name="Livros")

        categories = Category.objects.all()
        self.assertEqual(categories[0].name, "Acessórios")
        self.assertEqual(categories[1].name, "Livros")
        self.assertEqual(categories[2].name, "Roupas")

    def test_timestamps_on_update(self):
        """Testa se created_at e updated_at (com auto_now=True) funcionam."""
        category = Category.objects.create(name="Categoria Original")

        # Logo após a criação, a diferença deve ser mínima
        time_difference = category.updated_at - category.created_at
        self.assertLess(time_difference, timedelta(seconds=1))

        # Pausa para garantir que o timestamp de atualização mude
        sleep(0.1)

        # Atualiza o objeto
        category.name = "Categoria Atualizada"
        category.save()

        # Agora, o timestamp de atualização deve ser maior que o de criação
        self.assertGreater(category.updated_at, category.created_at)
