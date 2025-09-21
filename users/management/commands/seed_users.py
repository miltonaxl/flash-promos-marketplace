from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from stores.models import Store
from faker import Faker
import random
import time

fake = Faker()
User = get_user_model()

class Command(BaseCommand):
    help = 'Seed users data'
    
    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=4000, help='Number of users to create')
        parser.add_argument('--nearby-percentage', type=int, default=50, help='Percentage of users near stores')
    
    def handle(self, *args, **options):
        count = options['count']
        nearby_percentage = options['nearby_percentage']
        
        self.stdout.write(f'Creating {count} users ({nearby_percentage}% near stores)...')
        
        stores = list(Store.objects.all())
        if not stores:
            self.stdout.write(self.style.ERROR('No stores found. Please run seed_stores first.'))
            return
        
        nearby_count = int(count * nearby_percentage / 100)
        far_count = count - nearby_count
        
        # Precompute password hash once for all users
        password_hash = make_password('testpass123')
        
        # Generate users in bulk
        users_to_create = []
        
        # Create a timestamp to ensure uniqueness
        timestamp = int(time.time())
        
        # Create users near stores
        for i in range(nearby_count):
            store = random.choice(stores)
            
            # Generate locations near the store (within 2km)
            lat = store.latitude + random.uniform(-0.018, 0.018)
            lng = store.longitude + random.uniform(-0.018, 0.018)
            
            user_type = random.choices(
                ['new', 'frequent', 'regular'],
                weights=[0.3, 0.4, 0.3]
            )[0]
            
            # Generate unique username with timestamp
            username = f'u_n_{timestamp}_{i}'
            
            users_to_create.append(User(
                username=username,
                email=f'user_near_{timestamp}_{i}@example.com',
                password=password_hash,
                user_type=user_type,
                latitude=lat,
                longitude=lng,
                phone_number=fake.phone_number()[:15],
                first_name=fake.first_name(),
                last_name=fake.last_name()
            ))
            
            if i % 500 == 0 and i > 0:
                self.stdout.write(f'Prepared {i} nearby users...')
        
        # Create users far from stores
        for i in range(far_count):
            # Generate locations far from any store
            lat = random.uniform(4.0, 5.0)  # Far from Medellín/Bogotá/Cali
            lng = random.uniform(-77.0, -73.0)
            
            # Generate unique username with timestamp
            username = f'u_f_{timestamp}_{i}'
            
            users_to_create.append(User(
                username=username,
                email=f'user_far_{timestamp}_{i}@example.com',
                password=password_hash,
                user_type='regular',  # Most far users are regular users
                latitude=lat,
                longitude=lng,
                phone_number=fake.phone_number()[:15],
                first_name=fake.first_name(),
                last_name=fake.last_name()
            ))
            
            if i % 500 == 0 and i > 0:
                self.stdout.write(f'Prepared {i} far users...')
        
        # Bulk create all users
        batch_size = 500
        for i in range(0, len(users_to_create), batch_size):
            batch = users_to_create[i:i+batch_size]
            User.objects.bulk_create(batch, batch_size)
            self.stdout.write(f'Created {min(i+batch_size, len(users_to_create))} users...')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} users!'))