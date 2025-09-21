from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import FlashPromo, ProductReservation
from .serializers import FlashPromoSerializer, ProductReservationSerializer
from notifications.utils import is_user_near_store

class FlashPromoViewSet(viewsets.ModelViewSet):
    queryset = FlashPromo.objects.all()
    serializer_class = FlashPromoSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def reserve(self, request, pk=None):
        try:
            promo = self.get_object()
            user = request.user
            
            if not promo.is_active:
                return Response(
                    {'error': 'This promo is not active'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not self.is_user_eligible(user, promo):
                return Response(
                    {'error': 'You are not eligible for this promo'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if not is_user_near_store(user, promo.product.store):
                return Response(
                    {'error': 'You are not near the store'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            existing_reservation = ProductReservation.objects.filter(
                product=promo.product,
                reserved_until__gt=timezone.now(),
                is_completed=False
            ).exists()
            
            if existing_reservation:
                return Response(
                    {'error': 'Product is already reserved'}, 
                    status=status.HTTP_409_CONFLICT
                )
            
            reserved_until = timezone.now() + timezone.timedelta(minutes=1)
            reservation = ProductReservation.objects.create(
                product=promo.product,
                user=user,
                reserved_until=reserved_until
            )
            
            serializer = ProductReservationSerializer(reservation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except FlashPromo.DoesNotExist:
            return Response(
                {'error': 'Promo not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def is_user_eligible(self, user, promo):
        segments = promo.eligible_segments
        user_type = user.user_type
        
        if 'new_users' in segments and user_type == 'new':
            return True
        if 'frequent_buyers' in segments and user_type == 'frequent':
            return True
        
        return False

class ProductReservationViewSet(viewsets.ModelViewSet):
    queryset = ProductReservation.objects.all()
    serializer_class = ProductReservationSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        reservation = self.get_object()
        
        if reservation.reserved_until < timezone.now():
            return Response(
                {'error': 'Reservation has expired'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reservation.is_completed = True
        reservation.save()
        
        serializer = self.get_serializer(reservation)
        return Response(serializer.data)