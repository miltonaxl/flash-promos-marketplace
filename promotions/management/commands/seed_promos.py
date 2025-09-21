from django.core.management.base import BaseCommand
from django.utils import timezone
from stores.models import Product
from promotions.models import FlashPromo
from datetime import time

class Command(BaseCommand):
    help = 'Seed flash promotions data'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating flash promotions...')
        
        # Buscar productos de audífonos para crear promociones
        audio_products = Product.objects.filter(name__icontains='audífono')
        
        if not audio_products.exists():
            self.stdout.write(self.style.ERROR('No audio products found. Please run seed_stores first.'))
            return
        
        for product in audio_products:
            # Crear promo para audífonos como en el ejemplo del documento
            FlashPromo.objects.create(
                product=product,
                promo_price=499.99,
                start_time=time(17, 0),  # 5:00 PM
                end_time=time(19, 0),    # 7:00 PM
                eligible_segments=['new_users', 'frequent_buyers'],
                is_active=True
            )
            self.stdout.write(f'Created flash promo for {product.name} at {product.store.name}')
        
        self.stdout.write(self.style.SUCCESS('Flash promotions seeding completed!'))