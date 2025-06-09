from django.shortcuts import render
from django.views.generic import TemplateView
from products.models import Product
from categories.models import Category
from django.contrib.auth.views import LoginView
from django.contrib import messages
import requests


class ProductData:
    def __init__(self, id, title, selling_price, photo_url=None, is_api=False, obj=None):
        self.id = id
        self.title = title
        self.selling_price = selling_price
        self.photo_url = photo_url
        self.is_api = is_api
        self.obj = obj


class CustomLoginView(LoginView):
    def form_valid(self, form):
        response = super().form_valid(form)

        try:
            api_response = requests.post(
                'http://127.0.0.1:5000/api/v1/authetication/token/',
                json={
                    "username": form.cleaned_data['username'],
                    "password": form.cleaned_data['password']
                }
            )

            if api_response.status_code == 200:
                token_data = api_response.json()
                self.request.session['api_jwt_token'] = token_data['access']
            else:
                messages.warning(
                    self.request,
                    f"Falha na autenticação da API externa: {api_response.status_code} - {api_response.text}"
                )
        except Exception as e:
            messages.warning(self.request, f"Erro ao acessar a API externa: {e}")

        return response


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q = self.request.GET.get('q')
        category_name = self.request.GET.get('category')

        company_id = 1

        context['categories'] = [
            {'name': 'Mercearia'},
            {'name': 'Frutas'},
            {'name': 'Saladas'},
            {'name': 'Congelados'},
            {'name': 'Limpeza'},
        ]

        queryset = Product.objects.all()
        if category_name:
            queryset = queryset.filter(category__name__iexact=category_name)
        if q:
            queryset = queryset.filter(title__icontains=q)

        local_products = [
            ProductData(
                id=p.id,
                title=p.title,
                selling_price=p.selling_price,
                photo_url=p.photo.url if p.photo else None,
                is_api=False,
                obj=p,
            )
            for p in queryset
        ]

        api_products = []
        try:
            response = requests.get(
                f'http://127.0.0.1:5000/api/v1/public/products/{company_id}/',
                params={
                    'category': category_name if category_name else None,
                    'search': q if q else None
                },
                timeout=5,
            )
            response.raise_for_status()
            api_data = response.json()
            api_products = [
                ProductData(
                    id=item.get('id'),
                    title=item.get('title'),
                    selling_price=item.get('selling_price') or item.get('price') or 0,
                    photo_url=item.get('photo') or item.get('photo_url') or None,
                    is_api=True,
                )
                for item in api_data
            ]
        except Exception:
            api_products = []

        context['products'] = local_products + api_products
        context['query'] = q or ''
        context['selected_category'] = category_name or ''

        return context
