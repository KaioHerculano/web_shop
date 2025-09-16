from decimal import Decimal

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView

from products.models import Product


class ProductData:
    def __init__(
        self,
        id,
        title,
        selling_price,
        photo=None,
        is_api=False,
        obj=None,
        company_id=None,
        discount_price=None,
        rating=0,
    ):
        self.id = id
        self.title = title
        self.selling_price = selling_price
        self.photo = photo
        self.is_api = is_api
        self.obj = obj
        self.company_id = company_id
        self.discount_price = discount_price

        if (
            self.selling_price is not None
            and self.discount_price is not None
            and self.selling_price > Decimal("0")
        ):
            self.discount_percentage = int(
                ((self.selling_price - self.discount_price) / self.selling_price) * 100
            )
        else:
            self.discount_percentage = None
        self.rating = rating


class CustomLoginView(LoginView):
    def form_valid(self, form):
        response = super().form_valid(form)

        api_token_url = f"{settings.EXTERNAL_API_BASE_URL}/api/v1/authetication/token/"

        try:
            api_response = requests.post(
                api_token_url,
                json={
                    "username": form.cleaned_data["username"],
                    "password": form.cleaned_data["password"],
                },
            )

            if api_response.status_code == 200:
                token_data = api_response.json()
                self.request.session["api_jwt_token"] = token_data["access"]
            else:
                messages.warning(
                    self.request,
                    f"Falha na autenticação da API externa: {api_response.status_code} - {api_response.text}",
                )
        except Exception as error:
            messages.warning(self.request, f"Erro ao acessar a API externa: {error}")

        return response


class HomeView(TemplateView):
    """Exibe a página inicial com uma lista combinada de produtos locais e de uma API."""

    template_name = "home.html"

    @staticmethod
    def get_actual_price_for_sort(product_data):
        """
        Método estático para obter o preço real de um produto para ordenação.
        Prioriza o preço com desconto e trata valores inválidos.
        """
        price_to_compare = product_data.discount_price
        if price_to_compare is None:
            price_to_compare = product_data.selling_price

        if not isinstance(price_to_compare, Decimal):
            try:
                price_to_compare = Decimal(str(price_to_compare))
            except Exception:
                price_to_compare = Decimal("0.00")
        return price_to_compare

    def _transform_db_product(self, product, company_id):
        """Converte um objeto Product do banco de dados para o formato ProductData."""
        return ProductData(
            id=product.id,
            title=product.title,
            selling_price=product.selling_price,
            photo=product.photo.url if product.photo else None,
            is_api=False,
            obj=product,
            company_id=company_id,
            discount_price=product.discount_price,
            rating=getattr(product, "rating", 0),
        )

    def _transform_api_product(self, item, company_id, api_base_url):
        """Converte um dicionário de produto da API para o formato ProductData."""
        if item.get("quantity", 0) <= 0:
            return None

        raw_photo = item.get("photo") or item.get("photo_url")
        if raw_photo and not raw_photo.startswith("http"):
            if raw_photo.startswith("/media/"):
                raw_photo = f"{api_base_url}{raw_photo}"
            else:
                raw_photo = f"{api_base_url}/media/{raw_photo}"

        price_raw = item.get("selling_price") or item.get("price")
        selling_price = Decimal(str(price_raw)) if price_raw is not None else Decimal("0.00")

        discount_raw = item.get("discount_price")
        discount_price = Decimal(str(discount_raw)) if discount_raw is not None else None

        return ProductData(
            id=item.get("id"),
            title=item.get("title"),
            selling_price=selling_price,
            photo=raw_photo,
            is_api=True,
            company_id=company_id,
            discount_price=discount_price,
            rating=item.get("rating", 0),
        )

    def get_context_data(self, **kwargs):
        """
        Busca produtos locais e de uma API, combina-os, ordena e prepara para o template.
        """
        context = super().get_context_data(**kwargs)

        search_term = self.request.GET.get("q")
        selected_category = self.request.GET.get("category")
        company_id = 1
        api_base_url = settings.EXTERNAL_API_BASE_URL
        all_products = []

        local_query = Product.objects.filter(quantity__gt=0)
        if selected_category:
            local_query = local_query.filter(category__name__iexact=selected_category)
        if search_term:
            local_query = local_query.filter(title__icontains=search_term)

        for product in local_query:
            all_products.append(self._transform_db_product(product, company_id))

        try:
            params = {"category": selected_category, "search": search_term}
            response = requests.get(
                f"{api_base_url}/api/v1/public/products/{company_id}/",
                params={k: v for k, v in params.items() if v},
                timeout=5,
            )
            response.raise_for_status()
            api_product_list = response.json()

            for item in api_product_list:
                product_data = self._transform_api_product(item, company_id, api_base_url)
                if product_data:
                    all_products.append(product_data)
        except requests.RequestException as error:
            messages.warning(self.request, f"Não foi possível carregar produtos da API: {error}")

        all_products.sort(key=self.get_actual_price_for_sort)

        cheapest_products = []
        other_products = []
        for product in all_products:
            price = self.get_actual_price_for_sort(product)
            if price < Decimal("10.00") and len(cheapest_products) < 8:
                cheapest_products.append(product)
            else:
                other_products.append(product)

        context["cheapest_products"] = cheapest_products
        context["products"] = other_products
        context["query"] = search_term or ""
        context["selected_category"] = selected_category or ""
        context["categories"] = [
            {"name": "Mercearia"},
            {"name": "Frutas"},
            {"name": "Saladas"},
            {"name": "Congelados"},
            {"name": "Limpeza"},
            {"name": "Laticínios"},
            {"name": "Padaria"},
            {"name": "Bebidas"},
            {"name": "Carnes"},
        ]
        return context
