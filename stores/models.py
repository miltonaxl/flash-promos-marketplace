from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Store(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_stores')
    latitude = models.FloatField(null=True, blank=True)  # Cambiar de PointField
    longitude = models.FloatField(null=True, blank=True)  # Cambiar de PointField
    address = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_owner(self, user):
        """Verifica si el usuario es el propietario de la tienda"""
        return self.owner == user
    
    def __str__(self):
        return f"{self.name} - {self.owner.username}"

class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)