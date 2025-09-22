from django.db import models
from django.contrib.auth import get_user_model
from stores.models import Store
from promotions.models import FlashPromo

User = get_user_model()

class NotificationLog(models.Model):
    """Modelo para registrar todas las notificaciones enviadas"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    flash_promo = models.ForeignKey(FlashPromo, on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=50, default='flash_promo')
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    delivery_status = models.CharField(
        max_length=20, 
        choices=[
            ('sent', 'Sent'),
            ('delivered', 'Delivered'),
            ('failed', 'Failed')
        ],
        default='sent'
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['store', 'sent_at']),
            models.Index(fields=['user', 'sent_at']),
            models.Index(fields=['notification_type', 'sent_at']),
        ]
    
    def __str__(self):
        return f"Notification to {self.user.username} for {self.store.name} at {self.sent_at}"