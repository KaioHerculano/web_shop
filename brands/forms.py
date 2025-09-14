from django import forms

from . import models


class BrandForm(forms.ModelForm):
    class Meta:
        model = models.Brand
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter brand name"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter description (optional)",
                    "rows": 4,
                }
            ),
        }
        labels = {
            "name": "Nome",
            "description": "Descrição",
        }
