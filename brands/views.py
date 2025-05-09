from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from . import models, forms


class BrandListView(ListView):
    model = models.Brand
    template_name = 'brand_list.html'
    context_object_name = 'brands'


class BrandCreateView(CreateView):
    model = models.Brand
    template_name = 'brand_create.html'
    form_class = forms.BrandForm
    success_url = reverse_lazy('brand_list')



class BrandDetailView(DetailView):
    model = models.Brand
    template_name = 'brand_detail.html'


class BrandUpdateView(UpdateView):
    model = models.Brand
    template_name = 'brand_update.html'
    form_class = forms.BrandForm
    success_url = reverse_lazy('brand_list')


class BrandDeleteView(DeleteView):
    model = models.Brand
    template_name = 'brand_delete.html'
    success_url = reverse_lazy('brand_list')