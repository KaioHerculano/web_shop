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

        local_products = []
        for p in queryset:
            local_photo_url = None
            if p.photo:
                local_photo_url = p.photo.url
            
            local_products.append(
                ProductData(
                    id=p.id,
                    title=p.title,
                    selling_price=p.selling_price,
                    photo=local_photo_url,
                    is_api=False,
                    obj=p,
                    company_id=company_id,
                )
            )

        api_products = []
        api_base_url = "http://127.0.0.1:5000" 

        try:
            response = requests.get(
                f'{api_base_url}/api/v1/public/products/{company_id}/',
                params={
                    'category': category_name if category_name else None,
                    'search': q if q else None
                },
                timeout=5,
            )
            response.raise_for_status()
            api_data = response.json()
            api_products = [] 
            for item in api_data:
                processed_photo = item.get('photo') or item.get('photo_url') 
                
                if processed_photo:
                    if not processed_photo.startswith('http'):
                        if processed_photo.startswith('/media/'):
                            processed_photo = f'{api_base_url}{processed_photo}'
                        else:
                            processed_photo = f'{api_base_url}/media/{processed_photo}'

                api_products.append(
                    ProductData(
                        id=item.get('id'),
                        title=item.get('title'),
                        selling_price=item.get('selling_price') or item.get('price') or 0,
                        photo=processed_photo, 
                        is_api=True,
                        company_id=company_id,
                    )
                )
        except Exception as e:
            messages.error(self.request, f"Erro ao carregar produtos da API externa: {str(e)}")
            api_products = []

        context['products'] = local_products + api_products
        context['query'] = q or ''
        context['selected_category'] = category_name or ''

        return context
