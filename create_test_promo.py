from promotions.models import FlashPromo
from stores.models import Product
from django.utils import timezone
from datetime import time, timedelta

# Buscar un producto existente
product = Product.objects.first()

if product:
    # Crear una FlashPromo de prueba
    promo = FlashPromo.objects.create(
        product=product,
        promo_price=19.99,
        start_time=time(0, 0),
        end_time=time(23, 59),
        is_active=True
    )
    print(f'FlashPromo creada: {promo} - ID: {promo.id}')
else:
    print('No hay productos disponibles')