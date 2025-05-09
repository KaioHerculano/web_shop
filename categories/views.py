from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from . import models, forms


class CategoryListView(ListView):
    model = models.Category
    template_name = 'category_list.html'
    context_object_name = 'categories'


class CategoryCreateView(CreateView):
    model = models.Category
    template_name = 'category_create.html'
    form_class = forms.CategoryForm
    success_url = reverse_lazy('category_list')



class CategoryDetailView(DetailView):
    model = models.Category
    template_name = 'category_detail.html'


class CategoryUpdateView(UpdateView):
    model = models.Category
    template_name = 'category_update.html'
    form_class = forms.CategoryForm
    success_url = reverse_lazy('category_list')


class CategoryDeleteView(DeleteView):
    model = models.Category
    template_name = 'category_delete.html'
    success_url = reverse_lazy('category_list')
