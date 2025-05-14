# cart/cart.py
from products.models import Product  # ajuste conforme sua app

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product_id, quantity=1):
        product_id = str(product_id)
        if product_id in self.cart:
            self.cart[product_id] += quantity
        else:
            self.cart[product_id] = quantity
        self.save()

    def remove(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        self.session['cart'] = {}
        self.save()

    def save(self):
        self.session.modified = True

    def items(self):
        products = Product.objects.filter(id__in=self.cart.keys())
        items = []
        for product in products:
            quantity = self.cart[str(product.id)]
            subtotal = product.selling_price * quantity
            items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal,
            })
        return items

    def total(self):
        return sum(item['subtotal'] for item in self.items())
