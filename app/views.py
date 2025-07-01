from django.views.generic import TemplateView
from products.models import Product
from django.contrib.auth.views import LoginView
from django.contrib import messages
import requests


class ProductData:
    def __init__(self, id, title, selling_price, photo=None, is_api=False, obj=None, company_id=None):
        self.id = id
        self.title = title
        self.selling_price = selling_price
        self.photo = photo
        self.is_api = is_api
        self.obj = obj
        self.company_id = company_id


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
        except Exception as error:
            messages.warning(self.request, f"Erro ao acessar a API externa: {error}")

        return response


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        search_term = self.request.GET.get('q')
        selected_category = self.request.GET.get('category')
        company_id = 1

        # Categorias disponíveis
        context['categories'] = [
            {'name': 'Mercearia'},
            {'name': 'Frutas'},
            {'name': 'Saladas'},
            {'name': 'Congelados'},
            {'name': 'Limpeza'},
        ]

        # Produtos locais com estoque
        filtered_products = Product.objects.filter(quantity__gt=0)

        if selected_category:
            filtered_products = filtered_products.filter(category__name__iexact=selected_category)

        if search_term:
            filtered_products = filtered_products.filter(title__icontains=search_term)

        local_products = []
        for product in filtered_products:
            photo_url = product.photo.url if product.photo else None

            local_products.append(
                ProductData(
                    id=product.id,
                    title=product.title,
                    selling_price=product.selling_price,
                    photo=photo_url,
                    is_api=False,
                    obj=product,
                    company_id=company_id,
                )
            )

        # Produtos da API externa
        external_products = []
        api_base_url = "http://127.0.0.1:5000"

        try:
            api_response = requests.get(
                f'{api_base_url}/api/v1/public/products/{company_id}/',
                params={
                    'category': selected_category if selected_category else None,
                    'search': search_term if search_term else None
                },
                timeout=5,
            )
            api_response.raise_for_status()
            api_product_list = api_response.json()

            for product_item in api_product_list:
                if product_item.get('quantity', 0) <= 0:
                    continue

                raw_photo = product_item.get('photo') or product_item.get('photo_url')
                if raw_photo:
                    if not raw_photo.startswith('http'):
                        if raw_photo.startswith('/media/'):
                            raw_photo = f'{api_base_url}{raw_photo}'
                        else:
                            raw_photo = f'{api_base_url}/media/{raw_photo}'

                external_products.append(
                    ProductData(
                        id=product_item.get('id'),
                        title=product_item.get('title'),
                        selling_price=product_item.get('selling_price') or product_item.get('price') or 0,
                        photo=raw_photo,
                        is_api=True,
                        company_id=company_id,
                    )
                )
        except Exception as error:
            messages.error(self.request, f"Erro ao carregar produtos da API externa: {error}")
            external_products = []

        # Contexto final
        context['products'] = local_products + external_products
        context['query'] = search_term or ''
        context['selected_category'] = selected_category or ''

        return context
