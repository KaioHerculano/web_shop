from django import forms
from .models import Brand


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter brand name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter description (optional)', 'rows': 4}),
        }
