from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import requests
from . import models
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .forms import ProductForm


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
                    for item in data:
                        item['is_external'] = True
                        item['api_id'] = item['id']
                        api_products.append(item)
            except Exception as e:
                print("Erro ao acessar API externa:", e)

        return list(local_products) + api_products

class ProductDetailView(View):
    def get(self, request, *args, **kwargs):
        if 'external_id' in kwargs:
            return self.get_api_product(request, kwargs['external_id'])
        elif 'pk' in kwargs:
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
        try:
            api_url = f'http://127.0.0.1:5000/api/v1/public/products/1/{api_id}/'
            response = requests.get(api_url, timeout=5)
            if response.status_code == 404:
                messages.error(request, "Produto não encontrado na API")
                return redirect('product_list')
            response.raise_for_status()
            product_data = response.json()
            return render(request, 'product_detail.html', {
                'product': product_data,
                'is_external': True
            })
        except Exception as e:
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