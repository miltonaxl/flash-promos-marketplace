from rest_framework import serializers
from .models import FlashPromo, ProductReservation

class FlashPromoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlashPromo
        fields = '__all__'

class ProductReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReservation
        fields = '__all__'