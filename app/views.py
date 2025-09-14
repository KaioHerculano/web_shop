from decimal import Decimal

import requests
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

        try:
            api_response = requests.post(
                "http://127.0.0.1:5000/api/v1/authetication/token/",
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
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        search_term = self.request.GET.get("q")
        selected_category = self.request.GET.get("category")
        company_id = 1

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

        cheapest_products_list_raw = []

        products_for_offers_local_query = Product.objects.filter(quantity__gt=0)
        if selected_category:
            products_for_offers_local_query = products_for_offers_local_query.filter(
                category__name__iexact=selected_category
            )
        if search_term:
            products_for_offers_local_query = products_for_offers_local_query.filter(
                title__icontains=search_term
            )

        for product in products_for_offers_local_query:
            photo_url = product.photo.url if product.photo else None
            discount_price_local = getattr(product, "discount_price", None)
            rating_local = getattr(product, "rating", 0)
            cheapest_products_list_raw.append(
                ProductData(
                    id=product.id,
                    title=product.title,
                    selling_price=product.selling_price,
                    photo=photo_url,
                    is_api=False,
                    obj=product,
                    company_id=company_id,
                    discount_price=discount_price_local,
                    rating=rating_local,
                )
            )

        api_base_url = "http://127.0.0.1:5000"
        try:
            api_all_products_response = requests.get(
                f"{api_base_url}/api/v1/public/products/{company_id}/",
                params={
                    "category": selected_category if selected_category else None,
                    "search": search_term if search_term else None,
                },
                timeout=5,
            )
            api_all_products_response.raise_for_status()
            api_all_product_list = api_all_products_response.json()

            for product_item in api_all_product_list:
                if product_item.get("quantity", 0) <= 0:
                    continue

                raw_photo = product_item.get("photo") or product_item.get("photo_url")
                if raw_photo and not raw_photo.startswith("http"):
                    if raw_photo.startswith("/media/"):
                        raw_photo = f"{api_base_url}{raw_photo}"
                    else:
                        raw_photo = f"{api_base_url}/media/{raw_photo}"

                api_selling_price_raw = product_item.get("selling_price") or product_item.get(
                    "price"
                )
                api_selling_price = (
                    Decimal(str(api_selling_price_raw))
                    if api_selling_price_raw is not None
                    else Decimal("0.00")
                )

                api_discount_price_raw = product_item.get("discount_price")
                api_discount_price = (
                    Decimal(str(api_discount_price_raw))
                    if api_discount_price_raw is not None
                    else None
                )

                api_rating = product_item.get("rating", 0)

                cheapest_products_list_raw.append(
                    ProductData(
                        id=product_item.get("id"),
                        title=product_item.get("title"),
                        selling_price=api_selling_price,
                        photo=raw_photo,
                        is_api=True,
                        company_id=company_id,
                        discount_price=api_discount_price,
                        rating=api_rating,
                    )
                )
        except Exception as error:
            messages.warning(
                self.request, f"Erro ao carregar todos os produtos da API para ofertas: {error}"
            )

        def get_actual_price_for_sort(product_data):
            price_to_compare = product_data.discount_price
            if price_to_compare is None:
                price_to_compare = product_data.selling_price

            if not isinstance(price_to_compare, Decimal):
                try:
                    price_to_compare = Decimal(str(price_to_compare))
                except Exception:
                    price_to_compare = Decimal("0.00")
            return price_to_compare

        cheapest_products_list_raw.sort(key=get_actual_price_for_sort)

        products_below_10_reais = []
        for product_data in cheapest_products_list_raw:
            if get_actual_price_for_sort(product_data) < Decimal("10.00"):
                products_below_10_reais.append(product_data)

        context["cheapest_products"] = products_below_10_reais[:8]

        offered_product_ids = set()
        for p in context["cheapest_products"]:
            offered_product_ids.add((p.id, p.is_api))

        all_products_for_display = []

        products_from_db = Product.objects.filter(quantity__gt=0)
        if selected_category:
            products_from_db = products_from_db.filter(category__name__iexact=selected_category)
        if search_term:
            products_from_db = products_from_db.filter(title__icontains=search_term)

        for product_obj in products_from_db:
            product_data = ProductData(
                id=product_obj.id,
                title=product_obj.title,
                selling_price=product_obj.selling_price,
                photo=product_obj.photo.url if product_obj.photo else None,
                is_api=False,
                obj=product_obj,
                company_id=company_id,
                discount_price=getattr(product_obj, "discount_price", None),
                rating=getattr(product_obj, "rating", 0),
            )
            if (product_data.id, product_data.is_api) not in offered_product_ids:
                all_products_for_display.append(product_data)

        try:
            api_response_main = requests.get(
                f"{api_base_url}/api/v1/public/products/{company_id}/",
                params={
                    "category": selected_category if selected_category else None,
                    "search": search_term if search_term else None,
                },
                timeout=5,
            )
            api_response_main.raise_for_status()
            api_product_list_main = api_response_main.json()

            for product_item in api_product_list_main:
                if product_item.get("quantity", 0) <= 0:
                    continue

                raw_photo = product_item.get("photo") or product_item.get("photo_url")
                if raw_photo and not raw_photo.startswith("http"):
                    if raw_photo.startswith("/media/"):
                        raw_photo = f"{api_base_url}{raw_photo}"
                    else:
                        raw_photo = f"{api_base_url}/media/{raw_photo}"

                api_selling_price_raw = product_item.get("selling_price") or product_item.get(
                    "price"
                )
                api_selling_price = (
                    Decimal(str(api_selling_price_raw))
                    if api_selling_price_raw is not None
                    else Decimal("0.00")
                )

                api_discount_price_raw = product_item.get("discount_price")
                api_discount_price = (
                    Decimal(str(api_discount_price_raw))
                    if api_discount_price_raw is not None
                    else None
                )

                api_rating = product_item.get("rating", 0)

                product_data = ProductData(
                    id=product_item.get("id"),
                    title=product_item.get("title"),
                    selling_price=api_selling_price,
                    photo=raw_photo,
                    is_api=True,
                    company_id=company_id,
                    discount_price=api_discount_price,
                    rating=api_rating,
                )
                if (product_data.id, product_data.is_api) not in offered_product_ids:
                    all_products_for_display.append(product_data)

        except Exception as error:
            messages.error(
                self.request,
                f"Erro ao carregar produtos da API externa para exibição principal: {error}",
            )

        context["products"] = all_products_for_display
        context["query"] = search_term or ""
        context["selected_category"] = selected_category or ""

        return context
