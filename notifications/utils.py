import boto3
import json
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from users.models import User
from promotions.models import FlashPromo
from .models import NotificationLog
import math
def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula 
    dlat = lat2 - lat1 
    dlon = lon2 - lon1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    
    # Radius of earth in kilometers
    r = 6371
    return c * r

def send_flash_promo_notification(promo_id):
    try:
        promo = FlashPromo.objects.get(id=promo_id)
        
        # Obtener usuarios elegibles
        eligible_users = get_eligible_users_for_promo(promo)
        
        # Filtrar usuarios que ya recibieron notificación hoy
        today = timezone.now().date()
        users_to_notify = eligible_users.exclude(last_notification_sent=today)
        
        # Enviar notificaciones
        for user in users_to_notify:
            if is_user_near_store(user, promo.product.store):
                send_sns_notification(user, promo)
                user.last_notification_sent = today
                user.save()
                
    except FlashPromo.DoesNotExist:
        print(f"Promo with id {promo_id} does not exist")

def get_eligible_users_for_promo(promo):
    segments = promo.eligible_segments
    query = Q()
    
    if 'new_users' in segments:
        query |= Q(user_type='new')
    if 'frequent_buyers' in segments:
        query |= Q(user_type='frequent')
    
    return User.objects.filter(query)

def is_user_near_store(user, store, max_distance_km=2):
    """
    Check if user is within max_distance_km of the store
    using latitude and longitude coordinates
    """
    if (user.latitude is None or user.longitude is None or 
        store.latitude is None or store.longitude is None):
        return False
    
    # Calculate distance using Haversine formula
    distance = haversine_distance(
        user.latitude, user.longitude,
        store.latitude, store.longitude
    )
    
    return distance <= max_distance_km

def send_sns_notification(user, promo):
    sns_client = boto3.client(
        'sns',
        endpoint_url=settings.AWS_SNS_ENDPOINT_URL,
        region_name=settings.AWS_DEFAULT_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    
    message_text = f"Flash Promo available: {promo.product.name} at {promo.promo_price}"
    message = {
        'user_id': user.id,
        'promo_id': promo.id,
        'message': message_text
    }
    
    delivery_status = 'sent'
    try:
        sns_client.publish(
            TopicArn=settings.FLASH_PROMO_TOPIC_ARN,
            Message=json.dumps(message)
        )
        print(f"Notification sent to user {user.id} for promo {promo.id}")
        delivery_status = 'delivered'
    except Exception as e:
        print(f"Error sending notification: {e}")
        delivery_status = 'failed'
    
    # Registrar la notificación en el log
    NotificationLog.objects.create(
        user=user,
        store=promo.product.store,
        flash_promo=promo,
        notification_type='flash_promo',
        message=message_text,
        delivery_status=delivery_status
    )

# Función adicional para procesar mensajes de la cola SQS (si necesitas consumirlos)
def process_sqs_messages():
    """
    Optional: Function to process messages from SQS queue
    """
    sqs_client = boto3.client(
        'sqs',
        endpoint_url=settings.AWS_SQS_ENDPOINT_URL,
        region_name=settings.AWS_DEFAULT_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    
    queue_url = f"{settings.AWS_SQS_ENDPOINT_URL}/000000000000/flash-promo-notifications"
    
    try:
        response = sqs_client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=20
        )
        
        if 'Messages' in response:
            for message in response['Messages']:
                # Process the message
                message_body = json.loads(message['Body'])
                print(f"Received message: {message_body}")
                
                # Delete the message from queue after processing
                sqs_client.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=message['ReceiptHandle']
                )
                
    except Exception as e:
        print(f"Error processing SQS messages: {e}")