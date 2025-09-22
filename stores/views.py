from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Store, Product
from .serializers import StoreSerializer, ProductSerializer

class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    def get_permissions(self):
        """
        Permite acceso público para listar y obtener productos,
        requiere autenticación para crear, actualizar y eliminar
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        """Solo el owner de la tienda puede crear productos"""
        store_id = request.data.get('store')
        if not store_id:
            return Response(
                {'error': 'Store ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            store = Store.objects.get(id=store_id)
            if store.owner != request.user:
                return Response(
                    {'error': 'Only the store owner can create products'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
        except Store.DoesNotExist:
            return Response(
                {'error': 'Store not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """Solo el owner de la tienda puede actualizar productos"""
        product = self.get_object()
        if product.store.owner != request.user:
            return Response(
                {'error': 'Only the store owner can update this product'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        """Solo el owner de la tienda puede actualizar parcialmente productos"""
        product = self.get_object()
        if product.store.owner != request.user:
            return Response(
                {'error': 'Only the store owner can update this product'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().partial_update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Solo el owner de la tienda puede eliminar productos"""
        product = self.get_object()
        if product.store.owner != request.user:
            return Response(
                {'error': 'Only the store owner can delete this product'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().destroy(request, *args, **kwargs)