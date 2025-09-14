from django import forms

from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["customer_name", "address", "phone", "payment_method"]
        widgets = {
            "customer_name": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "payment_method": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {
            "customer_name": "Nome",
            "address": "Endereço",
            "phone": "Telefone",
            "payment_method": "Forma de Pagamento",
        }
