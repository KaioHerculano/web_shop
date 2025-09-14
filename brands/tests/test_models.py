from datetime import timedelta
from time import sleep

from django.test import TestCase

from brands.models import Brand


class BrandModelTest(TestCase):

    def test_brand_creation(self):
        """Testa a criação de uma marca e a representação __str__."""
        brand = Brand.objects.create(name="Marca Teste")
        # Usamos self.assertEqual em vez de assert
        self.assertEqual(Brand.objects.count(), 1)
        self.assertEqual(str(brand), "Marca Teste")

    def test_brand_ordering(self):
        """Testa se a ordenação padrão por nome está funcionando."""
        # Criamos os objetos dentro do próprio teste
        Brand.objects.create(name="Samsung")
        Brand.objects.create(name="Apple")
        Brand.objects.create(name="Xiaomi")

        brands = Brand.objects.all()
        self.assertEqual(brands[0].name, "Apple")
        self.assertEqual(brands[1].name, "Samsung")
        self.assertEqual(brands[2].name, "Xiaomi")

    def test_timestamps_on_update(self):
        """Testa se created_at e updated_at se comportam como esperado."""
        brand = Brand.objects.create(name="Marca Original")

        self.assertIsNotNone(brand.created_at)

        time_difference = brand.updated_at - brand.created_at
        self.assertLess(time_difference, timedelta(seconds=1))

        sleep(0.1)

        brand.name = "Marca Atualizada"
        brand.save()

        self.assertGreater(brand.updated_at, brand.created_at)
