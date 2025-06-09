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
            product_id = str(product.id)
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
            product_id = str(product_id)
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
        product_id = str(product_data['id'])
        if product_id in self.cart:
            current_qty = self.cart[product_id].get('quantity', 0)
            self.cart[product_id]['quantity'] = current_qty + quantity
        else:
            price = Decimal(str(product_data.get('selling_price', '0')))
            self.cart[product_id] = {
                'quantity': quantity,
                'type': 'api',
                'title': product_data.get('title', ''),
                'price': price,
                'brand': product_data.get('brand'),
                'category': product_data.get('category'),
                'description': product_data.get('description', ''),
                'serie_number': product_data.get('serie_number', ''),
            }
        self.save()

    def update(self, product_id, quantity):
        product_id = str(product_id)
        if product_id in self.cart:
            # Garanta que self.cart[product_id] é um dicionário antes de alterar 'quantity'
            if isinstance(self.cart[product_id], dict):
                self.cart[product_id]['quantity'] = quantity
            else:
                # Se for int, substitui por dicionário
                self.cart[product_id] = {
                    'quantity': quantity,
                    'type': 'local'  # ou api, conforme necessidade
                }
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
        items = []
        local_product_ids = [pid for pid, data in self.cart.items() if isinstance(data, dict) and data.get('type') == 'local']
        local_products = Product.objects.filter(id__in=local_product_ids)
        local_products_map = {str(prod.id): prod for prod in local_products}

        for product_id, data in self.cart.items():
            if not isinstance(data, dict):
                # Ignora dados incorretos
                continue
            quantity = data.get('quantity', 0)
            if data.get('type') == 'local':
                product = local_products_map.get(product_id)
                if product:
                    subtotal = product.selling_price * quantity
                    items.append({
                        'product': product,
                        'quantity': quantity,
                        'subtotal': subtotal,
                        'type': 'local',
                    })
            elif data.get('type') == 'api':
                price = data.get('price', Decimal('0'))
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
        total = sum(Decimal(item['subtotal']) for item in self.items())
        return total
