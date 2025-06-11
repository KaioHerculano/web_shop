from products.models import Product
from decimal import Decimal

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product_id=None, product=None, quantity=1):
        # Permite adicionar produto local (com product_id) ou produto da API (product dict)
        if product:
            product_id = f"local-{product.id}"
            # produto local é identificado por 'local' no type
            if product_id in self.cart:
                current_qty = self.cart[product_id].get('quantity', 0)
                self.cart[product_id]['quantity'] = current_qty + quantity
            else:
                self.cart[product_id] = {
                    'quantity': quantity,
                    'type': 'local'
                }
        else:
            product_id = f"local-{product_id}"
            if product_id in self.cart:
                current_qty = self.cart[product_id].get('quantity', 0)
                self.cart[product_id]['quantity'] = current_qty + quantity
            else:
                self.cart[product_id] = {
                    'quantity': quantity,
                    'type': 'local'
                }
        self.save()

    def add_api_product(self, product_data, quantity=1):
        # Converta todos os campos Decimal para float
        for key, value in product_data.items():
            if isinstance(value, Decimal):
                product_data[key] = float(value)

        product_id = f"api-{product_data['id']}"
        if product_id in self.cart:
            current_qty = self.cart[product_id].get('quantity', 0)
            self.cart[product_id]['quantity'] = current_qty + quantity
        else:
            self.cart[product_id] = {
                'quantity': quantity,
                'type': 'api',
                'title': product_data.get('title', ''),
                'price': product_data.get('selling_price', 0),
                'brand': product_data.get('brand'),
                'category': product_data.get('category'),
                'description': product_data.get('description', ''),
                'serie_number': product_data.get('serie_number', ''),
            }
        self.save()

    def update(self, product_id, quantity, product_type='local'):
        if product_type == 'local':
            key = f"local-{product_id}"
        else:
            key = f"api-{product_id}"
        if key in self.cart:
            if isinstance(self.cart[key], dict):
                self.cart[key]['quantity'] = quantity
            else:
                self.cart[key] = {
                    'quantity': quantity,
                    'type': product_type
                }
            self.save()

    def remove(self, product_id, product_type='local'):
        if product_type == 'local':
            key = f"local-{product_id}"
        else:
            key = f"api-{product_id}"
        if key in self.cart:
            del self.cart[key]
            self.save()

    def clear(self):
        self.session['cart'] = {}
        self.save()

    def save(self):
        self.session.modified = True

    def items(self):
        items = []
        # Só pega os ids locais que começam com 'local-'
        local_product_ids = [
            pid.split('-', 1)[1]
            for pid, data in self.cart.items()
            if isinstance(data, dict) and data.get('type') == 'local' and pid.startswith('local-')
        ]
        local_products = Product.objects.filter(id__in=local_product_ids)
        local_products_map = {str(prod.id): prod for prod in local_products}

        for product_id, data in self.cart.items():
            if not isinstance(data, dict):
                continue
            quantity = data.get('quantity', 0)
            if data.get('type') == 'local' and product_id.startswith('local-'):
                real_id = product_id.split('-', 1)[1]
                product = local_products_map.get(real_id)
                if product:
                    subtotal = product.selling_price * quantity
                    items.append({
                        'product': product,
                        'quantity': quantity,
                        'subtotal': subtotal,
                        'type': 'local',
                    })
            elif data.get('type') == 'api' and product_id.startswith('api-'):
                price = data.get('price', 0)
                try:
                    price = Decimal(str(price))
                except Exception:
                    price = Decimal('0')
                subtotal = price * quantity
                items.append({
                    'product': {
                        'id': product_id,
                        'title': data.get('title'),
                        'price': price,
                        'brand': data.get('brand'),
                        'category': data.get('category'),
                        'description': data.get('description'),
                        'serie_number': data.get('serie_number'),
                    },
                    'quantity': quantity,
                    'subtotal': subtotal,
                    'type': 'api',
                })
        return items

    def total(self):
        total = sum(item['subtotal'] if isinstance(item['subtotal'], Decimal) else Decimal(str(item['subtotal'])) for item in self.items())
        return total
