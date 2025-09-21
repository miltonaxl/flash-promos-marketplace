from django.db import models

class Store(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)  # Cambiar de PointField
    longitude = models.FloatField(null=True, blank=True)  # Cambiar de PointField
    address = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)