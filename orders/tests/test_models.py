from django.core.exceptions import ValidationError
from django.test import TestCase

from orders.models import Order


class OrderModelTest(TestCase):
    def test_create_order(self):
        order = Order.objects.create(
            customer_name="Kaio Herculano",
            address="Rua Exemplo, 123",
            phone="11999999999",
            payment_method="pix",
        )
        self.assertEqual(order.customer_name, "Kaio Herculano")
        self.assertEqual(order.address, "Rua Exemplo, 123")
        self.assertEqual(order.phone, "11999999999")
        self.assertEqual(order.payment_method, "pix")
        self.assertIsNotNone(order.created_at)

    def test_str_method(self):
        order = Order.objects.create(
            customer_name="Kaio Herculano",
            address="Rua Exemplo, 123",
            phone="11999999999",
            payment_method="pix",
        )
        expected_str = f"Pedido {order.id} - Kaio Herculano"
        self.assertEqual(str(order), expected_str)

    def test_payment_method_choices_validation(self):
        order = Order(
            customer_name="Kaio Herculano",
            address="Rua Exemplo, 123",
            phone="11999999999",
            payment_method="dinheiro_invalido",
        )
        with self.assertRaises(ValidationError):
            order.full_clean()
