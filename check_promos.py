from django.utils import timezone
from promotions.models import FlashPromo

print(f'Hora actual: {timezone.now().time()}')
promos = FlashPromo.objects.filter(is_active=True)
print(f'FlashPromos activas: {promos.count()}')

for p in promos:
    print(f'Promo {p.id}: start={p.start_time}, end={p.end_time}')
    
# Verificar si la hora actual está en el rango
now = timezone.now().time()
matching_promos = FlashPromo.objects.filter(
    start_time__lte=now,
    end_time__gte=now,
    is_active=True
)
print(f'Promos que coinciden con la hora actual: {matching_promos.count()}')