from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch, MagicMock
from decimal import Decimal
from datetime import date, time
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
import json

from users.models import User
from stores.models import Store, Product
from promotions.models import FlashPromo
from notifications.models import NotificationLog
from notifications.utils import (
    haversine_distance,
    send_flash_promo_notification,
    get_eligible_users_for_promo,
    is_user_near_store,
    send_sns_notification,
    process_sqs_messages
)


class HaversineDistanceTest(TestCase):
    """Tests para la función de cálculo de distancia haversine"""
    
    def test_haversine_distance_same_point(self):
        """Test distancia entre el mismo punto"""
        distance = haversine_distance(40.7831, -73.9712, 40.7831, -73.9712)
        self.assertEqual(distance, 0.0)
    
    def test_haversine_distance_known_points(self):
        """Test distancia entre puntos conocidos"""
        # Distancia aproximada entre Times Square y Central Park (NYC)
        lat1, lon1 = 40.7580, -73.9855  # Times Square
        lat2, lon2 = 40.7829, -73.9654  # Central Park
        
        distance = haversine_distance(lat1, lon1, lat2, lon2)
        
        # La distancia debería ser aproximadamente 3 km
        self.assertAlmostEqual(distance, 3.0, delta=1.0)
    
    def test_haversine_distance_different_hemispheres(self):
        """Test distancia entre diferentes hemisferios"""
        lat1, lon1 = 40.7831, -73.9712  # NYC
        lat2, lon2 = -33.8688, 151.2093  # Sydney
        
        distance = haversine_distance(lat1, lon1, lat2, lon2)
        
        # La distancia debería ser muy grande (más de 15,000 km)
        self.assertGreater(distance, 15000)


class GetEligibleUsersTest(TestCase):
    """Tests para obtener usuarios elegibles para promociones"""
    
    def setUp(self):
        # Crear usuario owner para la tienda
        self.owner = User.objects.create_user(
            username='storeowner',
            email='owner@test.com',
            password='testpass123'
        )
        
        self.store = Store.objects.create(
            name='Test Store',
            address='123 Test St',
            latitude=40.7831,
            longitude=-73.9712,
            owner=self.owner
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            description='Test product description',
            original_price=Decimal('100.00'),
            store=self.store
        )
        
        # Crear usuarios de diferentes tipos
        self.new_user = User.objects.create(
            username='newuser',
            email='new@test.com',
            user_type='new',
            latitude=40.7831,
            longitude=-73.9712
        )
        
        self.frequent_user = User.objects.create(
            username='frequentuser',
            email='frequent@test.com',
            user_type='frequent',
            latitude=40.7831,
            longitude=-73.9712
        )
        
        self.premium_user = User.objects.create(
            username='premiumuser',
            email='premium@test.com',
            user_type='regular',  # Cambiar a 'regular' ya que 'premium' no está en las opciones
            latitude=40.7831,
            longitude=-73.9712
        )
    
    def test_get_eligible_users_new_users(self):
        """Test obtener usuarios nuevos elegibles"""
        promo = FlashPromo.objects.create(
            product=self.product,
            promo_price=Decimal('80.00'),
            start_time=time(9, 0),
            end_time=time(18, 0),
            eligible_segments=['new_users'],
            is_active=True
        )
        
        eligible_users = get_eligible_users_for_promo(promo)
        
        self.assertIn(self.new_user, eligible_users)
        self.assertNotIn(self.frequent_user, eligible_users)
        self.assertNotIn(self.premium_user, eligible_users)
    
    def test_get_eligible_users_frequent_buyers(self):
        """Test obtener compradores frecuentes elegibles"""
        promo = FlashPromo.objects.create(
            product=self.product,
            promo_price=Decimal('80.00'),
            start_time=time(9, 0),
            end_time=time(18, 0),
            eligible_segments=['frequent_buyers'],
            is_active=True
        )
        
        eligible_users = get_eligible_users_for_promo(promo)
        
        self.assertNotIn(self.new_user, eligible_users)
        self.assertIn(self.frequent_user, eligible_users)
        self.assertNotIn(self.premium_user, eligible_users)
    
    def test_get_eligible_users_multiple_segments(self):
        """Test obtener usuarios de múltiples segmentos"""
        promo = FlashPromo.objects.create(
            product=self.product,
            promo_price=Decimal('80.00'),
            start_time=time(9, 0),
            end_time=time(18, 0),
            eligible_segments=['new_users', 'frequent_buyers'],
            is_active=True
        )
        
        eligible_users = get_eligible_users_for_promo(promo)
        
        self.assertIn(self.new_user, eligible_users)
        self.assertIn(self.frequent_user, eligible_users)
        self.assertNotIn(self.premium_user, eligible_users)


class IsUserNearStoreTest(TestCase):
    """Tests para verificar proximidad de usuario a tienda"""
    
    def setUp(self):
        # Crear usuario owner para la tienda
        self.owner = User.objects.create_user(
            username='storeowner2',
            email='owner2@test.com',
            password='testpass123'
        )
        
        self.store = Store.objects.create(
            name='Test Store',
            address='123 Test St',
            latitude=40.7831,
            longitude=-73.9712,
            owner=self.owner
        )
    
    def test_user_near_store_within_distance(self):
        """Test usuario cerca de la tienda (dentro del rango)"""
        user = User.objects.create(
            username='nearuser',
            email='near@test.com',
            latitude=40.7831,  # Misma ubicación
            longitude=-73.9712
        )
        
        is_near = is_user_near_store(user, self.store, max_distance_km=2)
        self.assertTrue(is_near)
    
    def test_user_far_from_store(self):
        """Test usuario lejos de la tienda (fuera del rango)"""
        user = User.objects.create(
            username='faruser',
            email='far@test.com',
            latitude=40.7505,  # Ubicación diferente
            longitude=-73.9934
        )
        
        is_near = is_user_near_store(user, self.store, max_distance_km=1)
        self.assertFalse(is_near)
    
    def test_user_no_coordinates(self):
        """Test usuario sin coordenadas"""
        user = User.objects.create(
            username='nocoordsuser',
            email='nocoords@test.com',
            latitude=None,
            longitude=None
        )
        
        is_near = is_user_near_store(user, self.store)
        self.assertFalse(is_near)
    
    def test_store_no_coordinates(self):
        """Test tienda sin coordenadas"""
        # Crear usuario owner para la tienda
        owner = User.objects.create_user(
            username='nocoordsowner',
            email='nocoordsowner@test.com',
            password='testpass123'
        )
        
        store_no_coords = Store.objects.create(
            name='No Coords Store',
            address='456 No Coords St',
            latitude=None,
            longitude=None,
            owner=owner
        )
        
        user = User.objects.create(
            username='storeuser',
            email='user@test.com',
            latitude=40.7831,
            longitude=-73.9712
        )
        
        is_near = is_user_near_store(user, store_no_coords)
        self.assertFalse(is_near)


class SendSNSNotificationTest(TestCase):
    """Tests para envío de notificaciones SNS"""
    
    def setUp(self):
        # Crear usuario owner para la tienda
        self.owner = User.objects.create_user(
            username='storeowner3',
            email='owner3@test.com',
            password='testpass123'
        )
        
        self.store = Store.objects.create(
            name='Test Store',
            address='123 Test St',
            latitude=40.7831,
            longitude=-73.9712,
            owner=self.owner
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            description='Test product description',
            original_price=Decimal('100.00'),
            store=self.store
        )
        
        self.user = User.objects.create(
            username='snsuser',
            email='test@test.com',
            latitude=40.7831,
            longitude=-73.9712
        )
        
        self.promo = FlashPromo.objects.create(
            product=self.product,
            promo_price=Decimal('80.00'),
            start_time=time(9, 0),
            end_time=time(18, 0),
            eligible_segments=['new_users'],
            is_active=True
        )
    
    @patch('notifications.utils.boto3.client')
    def test_send_sns_notification_success(self, mock_boto_client):
        """Test envío exitoso de notificación SNS"""
        mock_sns = MagicMock()
        mock_boto_client.return_value = mock_sns
        
        send_sns_notification(self.user, self.promo)
        
        # Verificar que se llamó a boto3.client
        mock_boto_client.assert_called_once()
        
        # Verificar que se llamó a publish
        mock_sns.publish.assert_called_once()
        
        # Verificar el contenido del mensaje
        call_args = mock_sns.publish.call_args
        message_str = call_args[1]['Message']
        message = json.loads(message_str)
        
        self.assertEqual(message['user_id'], self.user.id)
        self.assertEqual(message['promo_id'], self.promo.id)
        self.assertIn('Test Product', message['message'])
        self.assertIn('80.00', message['message'])
    
    @patch('notifications.utils.boto3.client')
    def test_send_sns_notification_error(self, mock_boto_client):
        """Test manejo de errores en envío de notificación SNS"""
        mock_sns = MagicMock()
        mock_sns.publish.side_effect = Exception('SNS Error')
        mock_boto_client.return_value = mock_sns
        
        # No debería lanzar excepción, solo imprimir error
        send_sns_notification(self.user, self.promo)
        
        mock_sns.publish.assert_called_once()


class NotificationStatsAPITest(APITestCase):
    """Tests para la API de estadísticas de notificaciones"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Crear usuario owner para la tienda
        self.owner = User.objects.create_user(
            username='storeowner_stats',
            email='owner_stats@test.com',
            password='testpass123'
        )
        
        self.store = Store.objects.create(
            name='Stats Test Store',
            address='123 Stats St',
            latitude=40.7831,
            longitude=-73.9712,
            owner=self.owner
        )
        
        self.product = Product.objects.create(
            name='Stats Test Product',
            description='Test product for stats',
            original_price=Decimal('100.00'),
            store=self.store
        )
        
        self.promo = FlashPromo.objects.create(
            product=self.product,
            promo_price=Decimal('80.00'),
            start_time=time(9, 0),
            end_time=time(18, 0),
            eligible_segments=['new_users'],
            is_active=True
        )
        
        # Crear algunos logs de notificaciones para testing
        self.user1 = User.objects.create(
            username='user1',
            email='user1@test.com'
        )
        
        self.user2 = User.objects.create(
            username='user2',
            email='user2@test.com'
        )
        
        # Crear logs de notificaciones
        NotificationLog.objects.create(
            user=self.user1,
            store=self.store,
            flash_promo=self.promo,
            notification_type='flash_promo',
            message='Test notification 1',
            delivery_status='delivered'
        )
        
        NotificationLog.objects.create(
            user=self.user2,
            store=self.store,
            flash_promo=self.promo,
            notification_type='flash_promo',
            message='Test notification 2',
            delivery_status='failed'
        )
    
    def test_store_stats_authenticated_owner(self):
        """Test obtener estadísticas con owner autenticado"""
        self.client.force_authenticate(user=self.owner)
        
        response = self.client.get('/api/notifications/store_stats/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertEqual(data['store_id'], self.store.id)
        self.assertEqual(data['store_name'], 'Stats Test Store')
        self.assertEqual(data['total_notifications_sent'], 2)
        self.assertIn('period_days', data)
        self.assertIn('start_date', data)
        self.assertIn('end_date', data)
        self.assertIn('notifications_by_status', data)
        self.assertIn('unique_users_notified', data)
        self.assertIn('notifications_by_day', data)
        self.assertIn('notifications_by_type', data)
    
    def test_store_stats_unauthenticated(self):
        """Test acceso sin autenticación"""
        response = self.client.get('/api/notifications/store_stats/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_store_stats_user_without_store(self):
        """Test usuario autenticado pero sin tienda"""
        user_without_store = User.objects.create_user(
            username='no_store_user',
            email='nostore@test.com',
            password='testpass123'
        )
        
        self.client.force_authenticate(user=user_without_store)
        
        response = self.client.get('/api/notifications/store_stats/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('No store found', response.json()['error'])


class SendFlashPromoNotificationTest(TestCase):
    """Tests para el flujo completo de envío de notificaciones"""
    
    def setUp(self):
        # Crear usuario owner para la tienda
        self.owner = User.objects.create_user(
            username='storeowner4',
            email='owner4@test.com',
            password='testpass123'
        )
        
        self.store = Store.objects.create(
            name='Test Store',
            address='123 Test St',
            latitude=40.7831,
            longitude=-73.9712,
            owner=self.owner
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            description='Test product description',
            original_price=Decimal('100.00'),
            store=self.store
        )
        
        self.user = User.objects.create(
            username='flashuser',
            email='test@test.com',
            user_type='new',
            latitude=40.7831,  # Cerca de la tienda
            longitude=-73.9712
        )
        
        self.promo = FlashPromo.objects.create(
            product=self.product,
            promo_price=Decimal('80.00'),
            start_time=time(9, 0),
            end_time=time(18, 0),
            eligible_segments=['new_users'],
            is_active=True
        )
    
    @patch('notifications.utils.send_sns_notification')
    def test_send_flash_promo_notification_success(self, mock_send_sns):
        """Test envío exitoso de notificación de flash promo"""
        send_flash_promo_notification(self.promo.id)
        
        # Verificar que se llamó a send_sns_notification
        mock_send_sns.assert_called_once_with(self.user, self.promo)
        
        # Verificar que se actualizó last_notification_sent
        self.user.refresh_from_db()
        self.assertEqual(self.user.last_notification_sent, timezone.now().date())
    
    def test_send_flash_promo_notification_nonexistent_promo(self):
        """Test manejo de promo inexistente"""
        # No debería lanzar excepción
        send_flash_promo_notification(99999)
    
    @patch('notifications.utils.send_sns_notification')
    def test_send_flash_promo_notification_already_notified_today(self, mock_send_sns):
        """Test usuario ya notificado hoy"""
        # Marcar usuario como ya notificado hoy
        self.user.last_notification_sent = timezone.now().date()
        self.user.save()
        
        send_flash_promo_notification(self.promo.id)
        
        # No debería enviar notificación
        mock_send_sns.assert_not_called()
    
    @patch('notifications.utils.send_sns_notification')
    def test_send_flash_promo_notification_user_far_from_store(self, mock_send_sns):
        """Test usuario lejos de la tienda"""
        # Mover usuario lejos de la tienda
        self.user.latitude = 41.0000  # Muy lejos
        self.user.longitude = -74.0000
        self.user.save()
        
        send_flash_promo_notification(self.promo.id)
        
        # No debería enviar notificación
        mock_send_sns.assert_not_called()


class ProcessSQSMessagesTest(TestCase):
    """Tests para procesamiento de mensajes SQS"""
    
    @patch('notifications.utils.boto3.client')
    def test_process_sqs_messages_success(self, mock_boto_client):
        """Test procesamiento exitoso de mensajes SQS"""
        mock_sqs = MagicMock()
        mock_boto_client.return_value = mock_sqs
        
        # Simular respuesta con mensajes
        mock_sqs.receive_message.return_value = {
            'Messages': [
                {
                    'Body': json.dumps({'test': 'message'}),
                    'ReceiptHandle': 'test-receipt-handle'
                }
            ]
        }
        
        process_sqs_messages()
        
        # Verificar que se llamó a receive_message
        mock_sqs.receive_message.assert_called_once()
        
        # Verificar que se llamó a delete_message
        mock_sqs.delete_message.assert_called_once_with(
            QueueUrl=mock_sqs.receive_message.call_args[1]['QueueUrl'],
            ReceiptHandle='test-receipt-handle'
        )
    
    @patch('notifications.utils.boto3.client')
    def test_process_sqs_messages_no_messages(self, mock_boto_client):
        """Test procesamiento sin mensajes"""
        mock_sqs = MagicMock()
        mock_boto_client.return_value = mock_sqs
        
        # Simular respuesta sin mensajes
        mock_sqs.receive_message.return_value = {}
        
        process_sqs_messages()
        
        # Verificar que se llamó a receive_message
        mock_sqs.receive_message.assert_called_once()
        
        # Verificar que NO se llamó a delete_message
        mock_sqs.delete_message.assert_not_called()
    
    @patch('notifications.utils.boto3.client')
    def test_process_sqs_messages_error(self, mock_boto_client):
        """Test manejo de errores en procesamiento SQS"""
        mock_sqs = MagicMock()
        mock_sqs.receive_message.side_effect = Exception('SQS Error')
        mock_boto_client.return_value = mock_sqs
        
        # No debería lanzar excepción
        process_sqs_messages()
        
        mock_sqs.receive_message.assert_called_once()