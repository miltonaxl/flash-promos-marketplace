from celery import shared_task
from django.utils import timezone
from .models import FlashPromo
from notifications.utils import send_flash_promo_notification, process_sqs_messages
from users.models import User


@shared_task
def check_active_promos():
    """
    Tarea periódica que verifica las promociones flash activas
    y envía notificaciones a usuarios elegibles.
    """
    try:
        now = timezone.now().time()
        active_promos = FlashPromo.objects.filter(
            start_time__lte=now,
            end_time__gte=now,
            is_active=True
        )
        
        for promo in active_promos:
            send_flash_promo_notification(promo.id)
            
        return f"Processed {active_promos.count()} active promos"
    except Exception as e:
        return f"Error checking active promos: {str(e)}"


@shared_task
def process_notification_queue():
    """
    Procesa la cola de mensajes SQS para notificaciones.
    """
    try:
        process_sqs_messages()
        return "SQS messages processed successfully"
    except Exception as e:
        return f"Error processing SQS messages: {str(e)}"


@shared_task
def send_promo_notification(promo_id):
    """
    Envía notificación para una promoción específica.
    """
    try:
        send_flash_promo_notification(promo_id)
        return f"Notification sent for promo {promo_id}"
    except Exception as e:
        return f"Error sending notification for promo {promo_id}: {str(e)}"


@shared_task
def cleanup_expired_promos():
    """
    Desactiva promociones expiradas.
    """
    try:
        now = timezone.now()
        expired_promos = FlashPromo.objects.filter(
            end_time__lt=now,
            is_active=True
        )
        
        count = expired_promos.count()
        expired_promos.update(is_active=False)
        
        return f"Deactivated {count} expired promos"
    except Exception as e:
        return f"Error cleaning up expired promos: {str(e)}"