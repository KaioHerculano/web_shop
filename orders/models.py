from django.db import models

class Order(models.Model):
    PAYMENT_CHOICES = [
        ('credit_card', 'Cartão de Crédito'),
        ('debit_card', 'Cartão de Débito'),
        ('pix', 'PIX'),
        ('boleto', 'Boleto'),
        ('cash', 'Dinheiro'),
    ]

    customer_name = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Pedido {self.id} - {self.customer_name}'
