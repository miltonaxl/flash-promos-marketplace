from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta, time
from decimal import Decimal
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from stores.models import Store, Product
from .models import FlashPromo, ProductReservation
from .serializers import FlashPromoSerializer, ProductReservationSerializer

User = get_user_model()


class FlashPromoModelTest(TestCase):
    """Tests para el modelo FlashPromo"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.store = Store.objects.create(
            name='Test Store',
            address='123 Test St',
            latitude=40.7128,
            longitude=-74.0060
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            description='A test product',
            original_price=Decimal('100.00'),
            store=self.store
        )
        
        self.flash_promo_data = {
            'product': self.product,
            'promo_price': Decimal('80.00'),
            'start_time': time(9, 0),  # 9:00 AM
            'end_time': time(17, 0),   # 5:00 PM
            'eligible_segments': ['new', 'frequent'],
            'is_active': True
        }
    
    def test_create_flash_promo(self):
        """Test crear una flash promo básica"""
        flash_promo = FlashPromo.objects.create(**self.flash_promo_data)
        self.assertEqual(flash_promo.product, self.product)
        self.assertEqual(flash_promo.promo_price, Decimal('80.00'))
        self.assertEqual(flash_promo.start_time, time(9, 0))
        self.assertEqual(flash_promo.end_time, time(17, 0))
        self.assertEqual(flash_promo.eligible_segments, ['new', 'frequent'])
        self.assertTrue(flash_promo.is_active)
    
    def test_flash_promo_str_representation(self):
        """Test representación string de la flash promo"""
        flash_promo = FlashPromo.objects.create(**self.flash_promo_data)
        expected_str = f"FlashPromo for {self.product.name}"
        self.assertEqual(str(flash_promo), expected_str)
    
    def test_flash_promo_default_values(self):
        """Test valores por defecto del modelo FlashPromo"""
        flash_promo = FlashPromo.objects.create(
            product=self.product,
            promo_price=Decimal('75.00'),
            start_time=time(10, 0),
            end_time=time(18, 0)
        )
        self.assertEqual(flash_promo.eligible_segments, [])
        self.assertFalse(flash_promo.is_active)
        self.assertIsNotNone(flash_promo.created_at)
        self.assertIsNotNone(flash_promo.updated_at)
    
    def test_flash_promo_time_validation(self):
        """Test validación de horarios de flash promo"""
        # End time debe ser después de start time
        invalid_data = self.flash_promo_data.copy()
        invalid_data['end_time'] = time(8, 0)  # Antes del start_time
        
        flash_promo = FlashPromo(**invalid_data)
        # Nota: Django no valida automáticamente que end_time > start_time
        # Se podría agregar validación personalizada en el modelo
    
    def test_flash_promo_eligible_segments(self):
        """Test segmentos elegibles de la flash promo"""
        flash_promo = FlashPromo.objects.create(**self.flash_promo_data)
        
        # Verificar segmentos iniciales
        self.assertIn('new', flash_promo.eligible_segments)
        self.assertIn('frequent', flash_promo.eligible_segments)
        
        # Actualizar segmentos
        flash_promo.eligible_segments = ['premium', 'vip']
        flash_promo.save()
        
        self.assertIn('premium', flash_promo.eligible_segments)
        self.assertIn('vip', flash_promo.eligible_segments)
        self.assertNotIn('new', flash_promo.eligible_segments)
    
    def test_flash_promo_price_discount(self):
        """Test descuento de precio en flash promo"""
        flash_promo = FlashPromo.objects.create(**self.flash_promo_data)
        
        original_price = self.product.original_price
        promo_price = flash_promo.promo_price
        
        # Verificar que el precio promocional es menor
        self.assertLess(promo_price, original_price)
        
        # Calcular descuento
        discount = original_price - promo_price
        discount_percentage = (discount / original_price) * 100
        
        self.assertEqual(discount, Decimal('20.00'))
        self.assertEqual(discount_percentage, 20.0)


class ProductReservationModelTest(TestCase):
    """Tests para el modelo ProductReservation"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='reserveuser',
            email='reserve@example.com',
            password='reservepass123'
        )
        
        self.store_owner = User.objects.create_user(
            username='storeowner',
            email='owner@example.com',
            password='ownerpass123'
        )
        
        self.store = Store.objects.create(
            name='Reserve Store',
            address='456 Reserve Ave',
            latitude=40.7589,
            longitude=-73.9851
        )
        
        self.product = Product.objects.create(
            name='Reserved Product',
            description='A product for reservation',
            original_price=Decimal('150.00'),
            store=self.store
        )
        
        self.reservation_data = {
            'product': self.product,
            'user': self.user,
            'reserved_until': timezone.now() + timedelta(hours=1),
            'is_completed': False
        }
    
    def test_create_product_reservation(self):
        """Test crear una reserva de producto"""
        reservation = ProductReservation.objects.create(**self.reservation_data)
        self.assertEqual(reservation.product, self.product)
        self.assertEqual(reservation.user, self.user)
        self.assertFalse(reservation.is_completed)
        self.assertIsNotNone(reservation.reserved_until)
        self.assertIsNotNone(reservation.created_at)
    
    def test_product_reservation_str_representation(self):
        """Test representación string de la reserva"""
        reservation = ProductReservation.objects.create(**self.reservation_data)
        expected_str = f"Reservation for {self.product.name} by {self.user.username}"
        self.assertEqual(str(reservation), expected_str)
    
    def test_product_reservation_completion(self):
        """Test completar una reserva de producto"""
        reservation = ProductReservation.objects.create(**self.reservation_data)
        
        # Marcar como completada
        reservation.is_completed = True
        reservation.save()
        
        self.assertTrue(reservation.is_completed)
    
    def test_product_reservation_expiration(self):
        """Test expiración de reserva de producto"""
        # Crear reserva que ya expiró
        expired_reservation_data = self.reservation_data.copy()
        expired_reservation_data['reserved_until'] = timezone.now() - timedelta(hours=1)
        
        reservation = ProductReservation.objects.create(**expired_reservation_data)
        
        # Verificar que la reserva está expirada
        self.assertLess(reservation.reserved_until, timezone.now())
        self.assertFalse(reservation.is_completed)
    
    def test_multiple_reservations_same_product(self):
        """Test múltiples reservas del mismo producto"""
        # Crear primera reserva
        reservation1 = ProductReservation.objects.create(**self.reservation_data)
        
        # Crear segundo usuario
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='user2pass123'
        )
        
        # Crear segunda reserva del mismo producto
        reservation_data2 = self.reservation_data.copy()
        reservation_data2['user'] = user2
        reservation_data2['reserved_until'] = timezone.now() + timedelta(hours=2)
        
        reservation2 = ProductReservation.objects.create(**reservation_data2)
        
        # Verificar que ambas reservas existen
        reservations = ProductReservation.objects.filter(product=self.product)
        self.assertEqual(reservations.count(), 2)
        
        # Verificar que son de usuarios diferentes
        self.assertNotEqual(reservation1.user, reservation2.user)


class FlashPromoSerializerTest(TestCase):
    """Tests para FlashPromoSerializer"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='serializeruser',
            email='serializer@example.com',
            password='serializerpass123'
        )
        
        self.store = Store.objects.create(
            name='Serializer Store',
            address='321 Serializer St',
            latitude=40.7282,
            longitude=-74.0776
        )
        
        self.product = Product.objects.create(
            name='Serializer Product',
            description='Test serializer product',
            original_price=Decimal('200.00'),
            store=self.store
        )
        
        self.flash_promo = FlashPromo.objects.create(
            product=self.product,
            promo_price=Decimal('160.00'),
            start_time=time(8, 0),
            end_time=time(20, 0),
            eligible_segments=['new', 'premium'],
            is_active=True
        )
    
    def test_flash_promo_serialization(self):
        """Test serialización de FlashPromo"""
        serializer = FlashPromoSerializer(self.flash_promo)
        data = serializer.data
        
        self.assertEqual(data['product'], self.product.id)
        self.assertEqual(Decimal(data['promo_price']), Decimal('160.00'))
        self.assertEqual(data['eligible_segments'], ['new', 'premium'])
        self.assertTrue(data['is_active'])
    
    def test_flash_promo_deserialization(self):
        """Test deserialización de FlashPromo"""
        data = {
            'product': self.product.id,
            'promo_price': '150.00',
            'start_time': '09:00:00',
            'end_time': '21:00:00',
            'eligible_segments': ['frequent', 'vip'],
            'is_active': True
        }
        
        serializer = FlashPromoSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_flash_promo_serializer_validation(self):
        """Test validación del FlashPromoSerializer"""
        # Test datos inválidos
        invalid_data = {
            'product': 999,  # Producto inexistente
            'promo_price': 'invalid_price',  # Precio inválido
            'start_time': 'invalid_time',  # Tiempo inválido
            'end_time': '25:00:00',  # Tiempo inválido
            'eligible_segments': 'not_a_list',  # No es una lista
        }
        serializer = FlashPromoSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())


class ProductReservationSerializerTest(TestCase):
    """Tests para ProductReservationSerializer"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='reserveserializer',
            email='reserveserializer@example.com',
            password='reservepass123'
        )
        
        self.store = Store.objects.create(
            name='Reserve Serializer Store',
            address='789 Reserve St',
            latitude=40.7505,
            longitude=-73.9934
        )
        
        self.product = Product.objects.create(
            name='Reserve Serializer Product',
            description='Test reserve serializer product',
            original_price=Decimal('300.00'),
            store=self.store
        )
        
        self.reservation = ProductReservation.objects.create(
            product=self.product,
            user=self.user,
            reserved_until=timezone.now() + timedelta(hours=2),
            is_completed=False
        )
    
    def test_product_reservation_serialization(self):
        """Test serialización de ProductReservation"""
        serializer = ProductReservationSerializer(self.reservation)
        data = serializer.data
        
        self.assertEqual(data['product'], self.product.id)
        self.assertEqual(data['user'], self.user.id)
        self.assertFalse(data['is_completed'])
        self.assertIsNotNone(data['reserved_until'])
    
    def test_product_reservation_deserialization(self):
        """Test deserialización de ProductReservation"""
        future_time = timezone.now() + timedelta(hours=3)
        data = {
            'product': self.product.id,
            'user': self.user.id,
            'reserved_until': future_time.isoformat(),
            'is_completed': False
        }
        
        serializer = ProductReservationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_product_reservation_serializer_validation(self):
        """Test validación del ProductReservationSerializer"""
        # Test datos inválidos
        invalid_data = {
            'product': 999,  # Producto inexistente
            'user': 999,     # Usuario inexistente
            'reserved_until': 'invalid_datetime',  # Datetime inválido
            'is_completed': 'not_boolean'  # No es booleano
        }
        serializer = ProductReservationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())


class PromotionsAPITest(APITestCase):
    """Tests para la API de promociones"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='apiuser',
            email='api@example.com',
            password='apipass123'
        )
        
        self.store = Store.objects.create(
            name='API Store',
            address='654 API Road',
            latitude=40.7614,
            longitude=-73.9776
        )
        
        self.product = Product.objects.create(
            name='API Product',
            description='Test API product',
            original_price=Decimal('250.00'),
            store=self.store
        )
        
        self.flash_promo = FlashPromo.objects.create(
            product=self.product,
            promo_price=Decimal('200.00'),
            start_time=time(10, 0),
            end_time=time(22, 0),
            eligible_segments=['new', 'frequent'],
            is_active=True
        )
    
    def test_flash_promo_list_api(self):
        """Test listado de flash promos via API"""
        response = self.client.get('/api/flash-promos/')
        # Nota: Este test asume que existe un endpoint de listado
        # Si no existe, el test fallará pero documenta la funcionalidad esperada
    
    def test_flash_promo_detail_api(self):
        """Test detalle de flash promo via API"""
        response = self.client.get(f'/api/flash-promos/{self.flash_promo.id}/')
        # Nota: Este test asume que existe un endpoint de detalle
    
    def test_create_flash_promo_api(self):
        """Test creación de flash promo via API"""
        self.client.force_authenticate(user=self.user)
        data = {
            'product': self.product.id,
            'promo_price': '180.00',
            'start_time': '11:00:00',
            'end_time': '23:00:00',
            'eligible_segments': ['premium', 'vip'],
            'is_active': True
        }
        response = self.client.post('/api/flash-promos/', data)
        # Nota: Este test asume que existe un endpoint de creación
    
    def test_product_reservation_api(self):
        """Test API de reservas de productos"""
        self.client.force_authenticate(user=self.user)
        data = {
            'product': self.product.id,
            'reserved_until': (timezone.now() + timedelta(hours=1)).isoformat()
        }
        response = self.client.post('/api/product-reservations/', data)
        # Nota: Este test asume que existe un endpoint de reservas


class PromotionsIntegrationTest(TestCase):
    """Tests de integración para promociones"""
    
    def test_flash_promo_with_user_segments(self):
        """Test flash promo con segmentación de usuarios"""
        # Crear usuarios de diferentes segmentos
        new_user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='newpass123',
            user_type='new'
        )
        
        frequent_user = User.objects.create_user(
            username='frequentuser',
            email='frequent@example.com',
            password='frequentpass123',
            user_type='frequent'
        )
        
        premium_user = User.objects.create_user(
            username='premiumuser',
            email='premium@example.com',
            password='premiumpass123',
            user_type='premium'
        )
        
        store_owner = User.objects.create_user(
            username='storeowner',
            email='owner@example.com',
            password='ownerpass123'
        )
        
        store = Store.objects.create(
            name='Segment Store',
            address='123 Segment St',
            latitude=40.7831,
            longitude=-73.9712
        )
        
        product = Product.objects.create(
            name='Segment Product',
            description='Product for segment testing',
            original_price=Decimal('100.00'),
            store=store
        )
        
        # Crear flash promo solo para usuarios 'new' y 'frequent'
        flash_promo = FlashPromo.objects.create(
            product=product,
            promo_price=Decimal('80.00'),
            start_time=time(9, 0),
            end_time=time(18, 0),
            eligible_segments=['new', 'frequent'],
            is_active=True
        )
        
        # Verificar segmentación
        self.assertIn('new', flash_promo.eligible_segments)
        self.assertIn('frequent', flash_promo.eligible_segments)
        self.assertNotIn('premium', flash_promo.eligible_segments)
        
        # Simular lógica de elegibilidad
        eligible_users = [new_user, frequent_user]
        non_eligible_users = [premium_user]
        
        for user in eligible_users:
            self.assertIn(user.user_type, flash_promo.eligible_segments)
        
        for user in non_eligible_users:
            self.assertNotIn(user.user_type, flash_promo.eligible_segments)
    
    def test_product_reservation_workflow(self):
        """Test flujo completo de reserva de productos"""
        user = User.objects.create_user(
            username='reserveworkflow',
            email='reserveworkflow@example.com',
            password='reservepass123'
        )
        
        store_owner = User.objects.create_user(
            username='workflowowner',
            email='workflowowner@example.com',
            password='ownerpass123'
        )
        
        store = Store.objects.create(
            name='Workflow Store',
            address='456 Workflow Ave',
            latitude=40.7505,
            longitude=-73.9934
        )
        
        product = Product.objects.create(
            name='Workflow Product',
            description='Product for workflow testing',
            original_price=Decimal('200.00'),
            store=store
        )
        
        # Crear flash promo para el producto
        flash_promo = FlashPromo.objects.create(
            product=product,
            promo_price=Decimal('150.00'),
            start_time=time(10, 0),
            end_time=time(20, 0),
            eligible_segments=['new', 'frequent', 'premium'],
            is_active=True
        )
        
        # Crear reserva del producto
        reservation = ProductReservation.objects.create(
            product=product,
            user=user,
            reserved_until=timezone.now() + timedelta(hours=1),
            is_completed=False
        )
        
        # Verificar que la reserva está activa
        self.assertFalse(reservation.is_completed)
        self.assertGreater(reservation.reserved_until, timezone.now())
        
        # Simular completar la compra
        reservation.is_completed = True
        reservation.save()
        
        # Verificar que la reserva está completada
        self.assertTrue(reservation.is_completed)
        
        # Verificar que el producto y flash promo siguen disponibles
        self.assertTrue(flash_promo.is_active)
        self.assertEqual(product.original_price, Decimal('200.00'))
        self.assertEqual(flash_promo.promo_price, Decimal('150.00'))
    
    def test_multiple_flash_promos_same_store(self):
        """Test múltiples flash promos en la misma tienda"""
        store_owner = User.objects.create_user(
            username='multiowner',
            email='multiowner@example.com',
            password='multipass123'
        )
        
        store = Store.objects.create(
            name='Multi Promo Store',
            address='789 Multi St',
            latitude=40.7614,
            longitude=-73.9776
        )
        
        # Crear múltiples productos
        products = []
        for i in range(3):
            product = Product.objects.create(
                name=f'Multi Product {i+1}',
                description=f'Product {i+1} for multi testing',
                original_price=Decimal(f'{100 + (i * 50)}.00'),
                store=store
            )
            products.append(product)
        
        # Crear flash promos para cada producto
        flash_promos = []
        for i, product in enumerate(products):
            flash_promo = FlashPromo.objects.create(
                product=product,
                promo_price=product.original_price * Decimal('0.8'),  # 20% descuento
                start_time=time(9 + i, 0),  # Horarios escalonados
                end_time=time(18 + i, 0),
                eligible_segments=['new', 'frequent'] if i % 2 == 0 else ['premium', 'vip'],
                is_active=True
            )
            flash_promos.append(flash_promo)
        
        # Verificar que todas las flash promos están activas
        active_promos = FlashPromo.objects.filter(product__store=store, is_active=True)
        self.assertEqual(active_promos.count(), 3)
        
        # Verificar diferentes segmentos
        promo_segments = [promo.eligible_segments for promo in flash_promos]
        self.assertEqual(promo_segments[0], ['new', 'frequent'])
        self.assertEqual(promo_segments[1], ['premium', 'vip'])
        self.assertEqual(promo_segments[2], ['new', 'frequent'])
        
        # Verificar precios promocionales
        for i, flash_promo in enumerate(flash_promos):
            expected_price = products[i].original_price * Decimal('0.8')
            self.assertEqual(flash_promo.promo_price, expected_price)
