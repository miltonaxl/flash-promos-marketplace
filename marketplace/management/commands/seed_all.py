from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Run all seeders'
    
    def add_arguments(self, parser):
        parser.add_argument('--store-count', type=int, default=3, help='Number of stores to create')
        parser.add_argument('--user-count', type=int, default=4000, help='Number of users to create')
        parser.add_argument('--nearby-percentage', type=int, default=50, help='Percentage of users near stores')
    
    def handle(self, *args, **options):
        self.stdout.write('Starting complete seeding process...')
        
        # Ejecutar seeders en orden
        call_command('seed_stores', count=options['store_count'])
        call_command('seed_users', count=options['user_count'], nearby_percentage=options['nearby_percentage'])
        call_command('seed_promos')
        
        self.stdout.write(self.style.SUCCESS('All seeders completed successfully!'))