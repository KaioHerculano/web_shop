from decimal import Decimal

from django.test import TestCase

from brands.models import Brand
from categories.models import Category
from products.models import Product


class ProductModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.brand = Brand.objects.create(name="Marca Exemplo")
        cls.category = Category.objects.create(name="Categoria Exemplo")

    def test_product_str_representation(self):
        """Testa se o método __str__ do Product retorna o título corretamente."""
        product = Product.objects.create(
            title="Notebook Pro",
            brand=self.brand,
            category=self.category,
            selling_price=Decimal("7500.00"),
            serie_number="NP12345",
        )

        self.assertEqual(str(product), "Notebook Pro")
