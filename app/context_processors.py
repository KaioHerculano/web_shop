def cart_items_count(request):
    cart = request.session.get('cart', {})
    count = sum(cart.values())  # Soma as quantidades diretamente
    return {'cart_items_count': count}