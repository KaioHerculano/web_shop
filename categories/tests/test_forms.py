from django.test import TestCase

from categories.forms import CategoryForm


class CategoryFormTest(TestCase):

    def test_form_is_valid_with_full_data(self):
        """Testa se o formulário é válido com todos os dados."""
        form_data = {"name": "Nova Categoria", "description": "Descrição da nova categoria."}
        form = CategoryForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_is_invalid_without_name(self):
        """Testa se o formulário é inválido se o nome estiver faltando."""
        form_data = {"description": "Categoria sem nome."}
        form = CategoryForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
