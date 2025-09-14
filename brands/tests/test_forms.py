from django.test import TestCase

from brands.forms import BrandForm


class BrandFormTest(TestCase):

    def test_form_valid(self):
        """Testa se o formulário é válido com todos os dados preenchidos."""
        form_data = {"name": "Nova Marca", "description": "Uma descrição."}
        form = BrandForm(data=form_data)
        # Usamos self.assertTrue para verificar condições verdadeiras
        self.assertTrue(form.is_valid())

    def test_form_name_is_required(self):
        """Testa se o formulário é inválido sem o campo 'name'."""
        form_data = {"description": "Sem nome."}
        form = BrandForm(data=form_data)
        # Usamos self.assertFalse para verificar condições falsas
        self.assertFalse(form.is_valid())
        # Usamos self.assertIn para verificar se um item está num container
        self.assertIn("name", form.errors)

    def test_form_description_is_optional(self):
        """Testa se o formulário é válido mesmo sem a descrição."""
        form_data = {"name": "Apenas Nome"}
        form = BrandForm(data=form_data)
        self.assertTrue(form.is_valid())
