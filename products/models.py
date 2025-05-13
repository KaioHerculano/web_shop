from django.db import models
from brands.models import Brand
from categories.models import Category


class Product(models.Model):
    title = models.CharField(max_length=300)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='brand_products')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='category_products')
    quantity = models.IntegerField(default=0)
    serie_number = models.CharField(max_length=300)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to='media/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title