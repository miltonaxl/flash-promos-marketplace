from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from stores.models import Store
from .models import NotificationLog
from .serializers import NotificationLogSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = NotificationLog.objects.all()
    serializer_class = NotificationLogSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def store_stats(self, request):
        """Obtener estadísticas de notificaciones por tienda del usuario autenticado"""
        days = int(request.query_params.get('days', 30))  # Por defecto últimos 30 días
        
        # Obtener la tienda del usuario autenticado
        try:
            store = Store.objects.get(owner=request.user)
        except Store.DoesNotExist:
            return Response(
                {'error': 'No store found for the authenticated user'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Calcular fecha de inicio
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Obtener estadísticas
        notifications = NotificationLog.objects.filter(
            store=store,
            sent_at__gte=start_date,
            sent_at__lte=end_date
        )
        
        stats = {
            'store_id': store.id,
            'store_name': store.name,
            'period_days': days,
            'start_date': start_date.date(),
            'end_date': end_date.date(),
            'total_notifications_sent': notifications.count(),
            'notifications_by_status': notifications.values('delivery_status').annotate(
                count=Count('id')
            ),
            'unique_users_notified': notifications.values('user').distinct().count(),
            'notifications_by_day': notifications.extra(
                select={'day': 'date(sent_at)'}
            ).values('day').annotate(
                count=Count('id')
            ).order_by('day'),
            'notifications_by_type': notifications.values('notification_type').annotate(
                count=Count('id')
            )
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def all_stores_summary(self, request):
        """Resumen de notificaciones para todas las tiendas (solo para admins)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admin users can view all stores summary'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        days = int(request.query_params.get('days', 30))
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Estadísticas por tienda
        store_stats = NotificationLog.objects.filter(
            sent_at__gte=start_date,
            sent_at__lte=end_date
        ).values(
            'store__id', 'store__name'
        ).annotate(
            total_notifications=Count('id'),
            unique_users=Count('user', distinct=True),
            successful_notifications=Count('id', filter=Q(delivery_status='delivered')),
            failed_notifications=Count('id', filter=Q(delivery_status='failed'))
        ).order_by('-total_notifications')
        
        summary = {
            'period_days': days,
            'start_date': start_date.date(),
            'end_date': end_date.date(),
            'total_stores_with_notifications': store_stats.count(),
            'stores_stats': list(store_stats)
        }
        
        return Response(summary)