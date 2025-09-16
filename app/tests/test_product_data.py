from decimal import Decimal

from django.test import TestCase

from app.views import ProductData


class ProductDataTest(TestCase):

    def test_calculo_desconto_sucesso(self):
        """
        Testa se o percentual de desconto é calculado corretamente.
        Cobre as linhas: 35-37
        """
        product = ProductData(
            id=1,
            title="Produto com Desconto",
            selling_price=Decimal("100.00"),
            discount_price=Decimal("80.00"),
        )
        self.assertEqual(product.discount_percentage, 20)

    def test_sem_preco_desconto(self):
        """
        Testa o caso em que não há preço com desconto.
        Cobre a linha: 39 (else)
        """
        product = ProductData(
            id=1,
            title="Produto sem Desconto",
            selling_price=Decimal("100.00"),
            discount_price=None,
        )
        self.assertIsNone(product.discount_percentage)

    def test_preco_venda_zero(self):
        """
        Testa o caso de borda em que o preço de venda é zero para evitar divisão por zero.
        Cobre a linha: 39 (else, devido à condição `self.selling_price > Decimal("0")`)
        """
        product = ProductData(
            id=1,
            title="Produto Grátis",
            selling_price=Decimal("0.00"),
            discount_price=Decimal("0.00"),
        )
        self.assertIsNone(product.discount_percentage)

    def test_sem_preco_venda(self):
        """
        Testa o caso em que o preço de venda é None.
        Cobre a linha: 39 (else)
        """
        product = ProductData(
            id=1, title="Produto sem preço", selling_price=None, discount_price=Decimal("10.00")
        )
        self.assertIsNone(product.discount_percentage)
