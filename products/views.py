from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import requests
from . import models
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .forms import ProductForm
from cart.cart import Cart

class AddApiProductToCartView(View):
    def post(self, request, product_id):
        token = request.session.get('api_jwt_token')
        if not token:
            messages.error(request, "Você precisa estar autenticado na API para adicionar este produto.")
            return redirect('home')
        
        api_url = f'http://127.0.0.1:5000/api/v1/products/{product_id}/'
        headers = {'Authorization': f'Bearer {token}'}

        try:
            response = requests.get(api_url, headers=headers, timeout=5)
            response.raise_for_status()
            product_data = response.json()
        except Exception as e:
            messages.error(request, f"Erro ao buscar produto na API: {e}")
            return redirect('home')
        
        # Cria ou obtém produto local baseado no external_id da API
        product, created = models.Product.objects.get_or_create(
            external_id=product_data['id'],
            defaults={
                'title': product_data.get('title', 'Produto da API'),
                'selling_price': product_data.get('selling_price', 0),
                'description': product_data.get('description', ''),
                'quantity': product_data.get('quantity', 0),
            }
        )
        
        quantity = int(request.POST.get('quantity', 1))
        cart = Cart(request)
        cart.add(product=product, quantity=quantity)

        messages.success(request, f"Produto '{product.title}' adicionado ao carrinho.")
        return redirect('cart_list')

class ProductListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = models.Product
    template_name = 'product_list.html'
    context_object_name = 'products'
    permission_required = 'products.view_product'

    def get_queryset(self):
        query = self.request.GET.get('q')
        local_products = models.Product.objects.all()
        if query:
            local_products = local_products.filter(title__icontains=query)

        api_products = []
        token = self.request.session.get('api_jwt_token')

        if token:
            try:
                headers = {'Authorization': f'Bearer {token}'}
                response = requests.get("http://127.0.0.1:5000/api/v1/products/", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    # Garantir que cada produto da API tem api_id
                    for item in data:
                        item['is_external'] = True
                        item['api_id'] = item['id']  # Campo essencial para o link
                        api_products.append(item)
            except Exception as e:
                print("Erro ao acessar API externa:", e)

        return list(local_products) + api_products

class ProductDetailView(View):
    """
    View customizada para exibir detalhe de produto local ou da API.
    """
    def get(self, request, *args, **kwargs):
        # Verifica se é um produto da API (external_id presente)
        if 'external_id' in kwargs:
            return self.get_api_product(request, kwargs['external_id'])
        elif 'pk' in kwargs:
            # Produto local
            return self.get_local_product(request, kwargs['pk'])
        else:
            messages.error(request, "Produto não encontrado")
            return redirect('product_list')
    
    def get_local_product(self, request, pk):
        try:
            product = models.Product.objects.get(pk=pk)
            return render(request, 'product_detail.html', {
                'product': product,
                'is_external': False
            })
        except models.Product.DoesNotExist:
            messages.error(request, "Produto local não encontrado")
            return redirect('product_list')
    
    def get_api_product(self, request, api_id):
        token = request.session.get('api_jwt_token')
        print("TOKEN:", token)
        if not token:
            messages.error(request, "Autenticação na API necessária")
            return redirect('product_list')
        
        try:
            api_url = f'http://127.0.0.1:5000/api/v1/products/{api_id}/'
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(api_url, headers=headers, timeout=5)
            print("API STATUS:", response.status_code)
            if response.status_code == 404:
                messages.error(request, "Produto não encontrado na API")
                return redirect('product_list')
                
            response.raise_for_status()
            product_data = response.json()
            print("API DATA:", product_data)
            return render(request, 'product_detail.html', {
                'product': product_data,
                'is_external': True
            })
        except Exception as e:
            print("API ERROR:", e)
            messages.error(request, f"Erro ao buscar produto na API: {str(e)}")
            return redirect('product_list')

class ProductCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = models.Product
    form_class = ProductForm
    template_name = 'product_create.html'
    success_url = reverse_lazy('product_list')
    permission_required = 'products.add_product'

class ProductUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = models.Product
    form_class = ProductForm
    template_name = 'product_update.html'
    success_url = reverse_lazy('product_list')
    permission_required = 'products.change_product'

class ProductDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = models.Product
    template_name = 'product_delete.html'
    success_url = reverse_lazy('product_list')
    permission_required = 'products.delete_product'