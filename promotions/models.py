from django.db import models
from django.contrib.auth import get_user_model
from stores.models import Product

class FlashPromo(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    promo_price = models.DecimalField(max_digits=10, decimal_places=2)
    start_time = models.TimeField()
    end_time = models.TimeField()
    eligible_segments = models.JSONField(default=list)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['is_active', 'start_time', 'end_time']),
        ]

    def __str__(self):
        return f"FlashPromo for {self.product.name}"

class ProductReservation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    reserved_until = models.DateTimeField()
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['reserved_until', 'is_completed']),
        ]

    def __str__(self):
        return f"Reservation for {self.product.name} by {self.user.username}"