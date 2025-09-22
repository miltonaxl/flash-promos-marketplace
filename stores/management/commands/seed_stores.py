from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from stores.models import Store, Product
from faker import Faker
import random

fake = Faker()
User = get_user_model()

class Command(BaseCommand):
    help = 'Seed stores and products data'
    
    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=3, help='Number of stores to create')
    
    def handle(self, *args, **options):
        count = options['count']
        self.stdout.write(f'Creating {count} stores with products...')
        
        stores_data = [
            {
                'name': 'TechShop Medellín Centro',
                'latitude': 6.2442,
                'longitude': -75.5812,
                'address': 'Carrera 50 # 53-45, Medellín',
                'products': [
                    {'name': 'Audífonos XYZ', 'price': 999.99, 'description': 'Audífonos de alta calidad con cancelación de ruido'},
                    {'name': 'Smartphone Alpha', 'price': 799.99, 'description': 'Teléfono inteligente de última generación'},
                    {'name': 'Laptop Gamma', 'price': 1299.99, 'description': 'Laptop potente para trabajo y gaming'},
                    {'name': 'Tablet Beta', 'price': 499.99, 'description': 'Tablet versátil para trabajo y entretenimiento'},
                    {'name': 'Smartwatch Delta', 'price': 299.99, 'description': 'Reloj inteligente con monitor de salud'},
                ]
            },
            {
                'name': 'TechShop Bogotá Norte',
                'latitude': 4.7109,
                'longitude': -74.0721,
                'address': 'Calle 85 # 12-45, Bogotá',
                'products': [
                    {'name': 'Audífonos ABC', 'price': 899.99, 'description': 'Audífonos premium con sonido surround'},
                    {'name': 'Smartphone Omega', 'price': 699.99, 'description': 'Teléfono con excelente cámara y batería'},
                    {'name': 'Laptop Sigma', 'price': 1199.99, 'description': 'Laptop ultradelgada y potente'},
                ]
            },
            {
                'name': 'TechShop Cali Sur',
                'latitude': 3.4516,
                'longitude': -76.5320,
                'address': 'Avenida 6N # 24-35, Cali',
                'products': [
                    {'name': 'Audífonos Pro', 'price': 1099.99, 'description': 'Audífonos profesionales para estudio'},
                    {'name': 'Smartphone Ultra', 'price': 899.99, 'description': 'Teléfono con pantalla AMOLED y 5G'},
                    {'name': 'Laptop Max', 'price': 1499.99, 'description': 'Laptop para creadores de contenido'},
                ]
            }
        ]
        
        for i, store_data in enumerate(stores_data[:count]):
            # Crear usuario owner para la tienda (o obtener si ya existe)
            owner, created = User.objects.get_or_create(
                username=f'owner_{i+1}',
                defaults={
                    'email': f'owner{i+1}@techshop.com',
                    'password': make_password('ownerpass123'),
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name(),
                    'user_type': 'regular',
                    'phone_number': fake.phone_number()[:15],
                    'latitude': store_data['latitude'],
                    'longitude': store_data['longitude']
                }
            )
            
            store, store_created = Store.objects.get_or_create(
                name=store_data['name'],
                defaults={
                    'latitude': store_data['latitude'],
                    'longitude': store_data['longitude'],
                    'address': store_data['address'],
                    'owner': owner,
                    'is_active': True
                }
            )
            
            for product_data in store_data['products']:
                product, product_created = Product.objects.get_or_create(
                    store=store,
                    name=product_data['name'],
                    defaults={
                        'description': product_data['description'],
                        'original_price': product_data['price'],
                        'is_available': True
                    }
                )
            
            action = "Created" if store_created else "Found existing"
            self.stdout.write(self.style.SUCCESS(f'{action} store: {store.name} with owner {owner.username} and {len(store_data["products"])} products'))
        
        self.stdout.write(self.style.SUCCESS('Stores and products seeding completed!'))