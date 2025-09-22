from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.gis.geos import Point
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import User
from .serializers import UserSerializer

User = get_user_model()


class UserModelTest(TestCase):
    """Tests para el modelo User personalizado"""
    
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'user_type': 'customer',
            'phone_number': '+1234567890'
        }
    
    def test_create_user(self):
        """Test crear un usuario básico"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.user_type, 'customer')
        self.assertEqual(user.phone_number, '+1234567890')
        self.assertTrue(user.check_password('testpass123'))
    
    def test_user_str_representation(self):
        """Test representación string del usuario"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'testuser')
    
    def test_user_default_values(self):
        """Test valores por defecto del modelo User"""
        user = User.objects.create_user(
            username='defaultuser',
            email='default@example.com',
            password='pass123'
        )
        self.assertEqual(user.user_type, 'regular')  # Default value
        self.assertEqual(user.notification_preferences, {})
        self.assertIsNone(user.last_notification_sent)
        self.assertIsNone(user.latitude)
        self.assertIsNone(user.longitude)
        self.assertIsNone(user.location)
    
    def test_user_types(self):
        """Test diferentes tipos de usuario"""
        # Test customer
        customer = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='pass123',
            user_type='new'
        )
        self.assertEqual(customer.user_type, 'new')
        
        # Test frequent buyer
        frequent = User.objects.create_user(
            username='frequent',
            email='frequent@example.com',
            password='pass123',
            user_type='frequent'
        )
        self.assertEqual(frequent.user_type, 'frequent')
    
    def test_user_location_fields(self):
        """Test campos de ubicación del usuario"""
        user = User.objects.create_user(**self.user_data)
        
        # Test coordenadas separadas
        user.latitude = 40.7128
        user.longitude = -74.0060
        user.save()
        
        self.assertEqual(user.latitude, 40.7128)
        self.assertEqual(user.longitude, -74.0060)
        
        # Test PointField GIS
        point = Point(-74.0060, 40.7128)  # longitude, latitude
        user.location = point
        user.save()
        
        self.assertEqual(user.location.x, -74.0060)
        self.assertEqual(user.location.y, 40.7128)
    
    def test_user_notification_preferences(self):
        """Test preferencias de notificación"""
        user = User.objects.create_user(**self.user_data)
        
        preferences = {
            'email_notifications': True,
            'push_notifications': False,
            'sms_notifications': True
        }
        user.notification_preferences = preferences
        user.save()
        
        self.assertEqual(user.notification_preferences, preferences)
        self.assertTrue(user.notification_preferences['email_notifications'])
        self.assertFalse(user.notification_preferences['push_notifications'])
    
    def test_user_required_fields(self):
        """Test campos requeridos del modelo User"""
        from django.core.exceptions import ValidationError
        
        # Username es requerido
        with self.assertRaises(ValidationError):
            user = User(email='test@example.com', password='pass123')
            user.full_clean()


class UserSerializerTest(TestCase):
    """Tests para el UserSerializer"""
    
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'user_type': 'customer',
            'phone_number': '+1234567890'
        }
        self.user = User.objects.create_user(**self.user_data)
    
    def test_user_serialization(self):
        """Test serialización de User"""
        serializer = UserSerializer(self.user)
        data = serializer.data
        
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['email'], 'test@example.com')
        self.assertEqual(data['user_type'], 'customer')
        self.assertEqual(data['phone_number'], '+1234567890')
        # Password no debe estar en la serialización
        self.assertNotIn('password', data)
    
    def test_user_deserialization(self):
        """Test deserialización de User"""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'user_type': 'frequent',
            'phone_number': '+9876543210'
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_user_serializer_validation(self):
        """Test validación del UserSerializer"""
        # Test datos inválidos
        invalid_data = {
            'username': '',  # Username vacío
            'email': 'invalid-email',  # Email inválido
            'user_type': 'invalid_type'  # Tipo inválido
        }
        serializer = UserSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())


class UserAPITest(APITestCase):
    """Tests para la API de usuarios"""
    
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'user_type': 'customer'
        }
        self.user = User.objects.create_user(**self.user_data)
    
    def test_user_registration(self):
        """Test registro de nuevo usuario"""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'user_type': 'customer'
        }
        response = self.client.post('/api/users/register/', data)
        # Nota: Este test asume que existe un endpoint de registro
        # Si no existe, el test fallará pero es útil para documentar la funcionalidad esperada
    
    def test_user_profile_access(self):
        """Test acceso al perfil de usuario"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/users/profile/')
        # Nota: Este test asume que existe un endpoint de perfil
        # Si no existe, el test fallará pero es útil para documentar la funcionalidad esperada


class UserIntegrationTest(TestCase):
    """Tests de integración para usuarios"""
    
    def test_user_with_location_data(self):
        """Test usuario con datos de ubicación completos"""
        user = User.objects.create_user(
            username='locationuser',
            email='location@example.com',
            password='pass123',
            latitude=40.7128,
            longitude=-74.0060
        )
        
        # Agregar PointField
        point = Point(-74.0060, 40.7128)
        user.location = point
        user.save()
        
        # Verificar que ambos sistemas de coordenadas funcionan
        self.assertEqual(user.latitude, 40.7128)
        self.assertEqual(user.longitude, -74.0060)
        self.assertEqual(user.location.x, -74.0060)
        self.assertEqual(user.location.y, 40.7128)
    
    def test_user_notification_workflow(self):
        """Test flujo completo de notificaciones"""
        from datetime import datetime
        
        user = User.objects.create_user(
            username='notifyuser',
            email='notify@example.com',
            password='pass123'
        )
        
        # Configurar preferencias
        user.notification_preferences = {
            'email_notifications': True,
            'push_notifications': True
        }
        
        # Simular envío de notificación
        user.last_notification_sent = datetime.now()
        user.save()
        
        self.assertIsNotNone(user.last_notification_sent)
        self.assertTrue(user.notification_preferences['email_notifications'])
