from django.test import TestCase

from orders.forms import OrderForm


class OrderFormTest(TestCase):
    def test_form_valid_data(self):
        form_data = {
            "customer_name": "Kaio Herculano",
            "address": "Rua Exemplo, 123",
            "phone": "11999999999",
            "payment_method": "pix",
        }
        form = OrderForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_without_fields(self):
        form = OrderForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("customer_name", form.errors)
        self.assertIn("address", form.errors)
        self.assertIn("phone", form.errors)
        self.assertIn("payment_method", form.errors)
