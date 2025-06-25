from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'brand', 'category', 'quantity', 'serie_number', 'selling_price', 'description', 'photo',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'brand': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.TextInput(attrs={'class': 'form-control'}),
            'serie_number': forms.TextInput(attrs={'class': 'form-control'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'data-mask': '000.000.000,00', 'data-mask-reverse': 'True'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),

        }
        labels = {
            'title': 'Titulo',
            'brand': 'Marca',
            'category': 'Categoria',
            'quantity': 'Quantidade',
            'serie_number': 'Numero de Serie',
            'selling_price': 'Preço de Venda',
            'description': 'Descrição',
            'photo': 'Foto do Produto',
        }