from rest_framework import serializers
from .models import NotificationLog

class NotificationLogSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)
    flash_promo_product_name = serializers.CharField(source='flash_promo.product.name', read_only=True)
    
    class Meta:
        model = NotificationLog
        fields = [
            'id', 'user', 'user_username', 'store', 'store_name', 
            'flash_promo', 'flash_promo_product_name', 'notification_type', 
            'message', 'sent_at', 'delivery_status'
        ]
        read_only_fields = ['sent_at']