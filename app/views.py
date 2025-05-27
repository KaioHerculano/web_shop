from django.shortcuts import render
from django.views.generic import TemplateView
from products.models import Product
from categories.models import Category


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        q = self.request.GET.get('q')
        category_name = self.request.GET.get('category')

        categories = Category.objects.all()
        context['categories'] = categories

        if category_name:
            products = Product.objects.filter(category__name__iexact=category_name)
        elif q:
            products = Product.objects.filter(title__icontains=q)
        else:
            products = Product.objects.all()

        context['products'] = products
        context['query'] = q or ''
        context['selected_category'] = category_name or ''
        return context
