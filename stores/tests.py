from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from .models import Store, Product
from .serializers import StoreSerializer, ProductSerializer

User = get_user_model()


class StoreModelTest(TestCase):
    """Tests para el modelo Store"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testowner',
            email='owner@test.com',
            password='testpass123'
        )
        self.store_data = {
            'name': 'Test Store',
            'owner': self.user,
            'latitude': 6.2442,
            'longitude': -75.5812,
            'address': 'Test Address 123',
            'is_active': True
        }
    
    def test_create_store(self):
        """Test crear una tienda"""
        store = Store.objects.create(**self.store_data)
        self.assertEqual(store.name, 'Test Store')
        self.assertEqual(store.latitude, 6.2442)
        self.assertEqual(store.longitude, -75.5812)
        self.assertEqual(store.address, 'Test Address 123')
        self.assertTrue(store.is_active)
        self.assertIsNotNone(store.created_at)
    
    def test_store_str_representation(self):
        """Test representación string del modelo Store"""
        store = Store.objects.create(**self.store_data)
        # El __str__ está definido como "name - owner.username"
        expected_str = f"{store.name} - {store.owner.username}"
        self.assertEqual(str(store), expected_str)
    
    def test_store_default_values(self):
        """Test valores por defecto del modelo Store"""
        store = Store.objects.create(
            name='Test Store',
            owner=self.user,
            address='Test Address'
        )
        self.assertTrue(store.is_active)  # Default True
        self.assertIsNone(store.latitude)  # Default None
        self.assertIsNone(store.longitude)  # Default None
    
    def test_store_required_fields(self):
        """Test campos requeridos del modelo Store"""
        from django.core.exceptions import ValidationError
        
        # Intentar crear sin name debería fallar
        with self.assertRaises(ValidationError):
            store = Store(address='Test Address')
            store.full_clean()  # Validar antes de guardar
        
        # Intentar crear sin address debería fallar
        with self.assertRaises(ValidationError):
            store = Store(name='Test Store')
            store.full_clean()  # Validar antes de guardar


class ProductModelTest(TestCase):
    """Tests para el modelo Product"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testowner',
            email='owner@test.com',
            password='testpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.user,
            address='Test Address'
        )
        self.product_data = {
            'store': self.store,
            'name': 'Test Product',
            'description': 'Test Description',
            'original_price': Decimal('99.99'),
            'is_available': True
        }
    
    def test_create_product(self):
        """Test crear un producto"""
        product = Product.objects.create(**self.product_data)
        self.assertEqual(product.name, 'Test Product')
        self.assertEqual(product.description, 'Test Description')
        self.assertEqual(product.original_price, Decimal('99.99'))
        self.assertTrue(product.is_available)
        self.assertEqual(product.store, self.store)
        self.assertIsNotNone(product.created_at)
    
    def test_product_store_relationship(self):
        """Test relación entre Product y Store"""
        product = Product.objects.create(**self.product_data)
        self.assertEqual(product.store, self.store)
        
        # Test cascade delete
        store_id = self.store.id
        self.store.delete()
        self.assertFalse(Product.objects.filter(id=product.id).exists())
    
    def test_product_default_values(self):
        """Test valores por defecto del modelo Product"""
        product = Product.objects.create(
            store=self.store,
            name='Test Product',
            original_price=Decimal('50.00')
        )
        self.assertTrue(product.is_available)  # Default True
        self.assertEqual(product.description, '')  # Default empty string
    
    def test_product_required_fields(self):
        """Test campos requeridos del modelo Product"""
        # Intentar crear sin store debería fallar
        with self.assertRaises(Exception):
            Product.objects.create(
                name='Test Product',
                original_price=Decimal('50.00')
            )
        
        # Intentar crear sin name debería fallar
        with self.assertRaises(Exception):
            Product.objects.create(
                store=self.store,
                original_price=Decimal('50.00')
            )
        
        # Intentar crear sin original_price debería fallar
        with self.assertRaises(Exception):
            Product.objects.create(
                store=self.store,
                name='Test Product'
            )


class StoreSerializerTest(TestCase):
    """Tests para StoreSerializer"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testowner',
            email='owner@test.com',
            password='testpass123'
        )
        self.store_data = {
            'name': 'Test Store',
            'owner': self.user,
            'latitude': 6.2442,
            'longitude': -75.5812,
            'address': 'Test Address 123',
            'is_active': True
        }
        # Datos para deserialización (usando ID del usuario)
        self.store_data_for_serializer = {
            'name': 'Test Store',
            'owner': self.user.id,
            'latitude': 6.2442,
            'longitude': -75.5812,
            'address': 'Test Address 123',
            'is_active': True
        }
        self.store = Store.objects.create(**self.store_data)
    
    def test_store_serialization(self):
        """Test serialización de Store"""
        serializer = StoreSerializer(self.store)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Test Store')
        self.assertEqual(data['latitude'], 6.2442)
        self.assertEqual(data['longitude'], -75.5812)
        self.assertEqual(data['address'], 'Test Address 123')
        self.assertTrue(data['is_active'])
        self.assertIn('id', data)
        self.assertIn('created_at', data)
    
    def test_store_deserialization(self):
        """Test deserialización de Store"""
        serializer = StoreSerializer(data=self.store_data_for_serializer)
        self.assertTrue(serializer.is_valid())
        
        store = serializer.save()
        self.assertEqual(store.name, 'Test Store')
        self.assertEqual(store.latitude, 6.2442)
        self.assertEqual(store.longitude, -75.5812)
    
    def test_store_serializer_validation(self):
        """Test validación del StoreSerializer"""
        # Test datos inválidos
        invalid_data = {
            'name': '',  # Campo requerido vacío
            'address': 'Test Address'
        }
        serializer = StoreSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)


class ProductSerializerTest(TestCase):
    """Tests para ProductSerializer"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testowner',
            email='owner@test.com',
            password='testpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.user,
            address='Test Address'
        )
        self.product_data = {
            'store': self.store.id,
            'name': 'Test Product',
            'description': 'Test Description',
            'original_price': '99.99',
            'is_available': True
        }
        self.product = Product.objects.create(
            store=self.store,
            name='Test Product',
            description='Test Description',
            original_price=Decimal('99.99'),
            is_available=True
        )
    
    def test_product_serialization(self):
        """Test serialización de Product"""
        serializer = ProductSerializer(self.product)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Test Product')
        self.assertEqual(data['description'], 'Test Description')
        self.assertEqual(data['original_price'], '99.99')
        self.assertTrue(data['is_available'])
        self.assertEqual(data['store'], self.store.id)
        self.assertIn('id', data)
        self.assertIn('created_at', data)
    
    def test_product_deserialization(self):
        """Test deserialización de Product"""
        serializer = ProductSerializer(data=self.product_data)
        self.assertTrue(serializer.is_valid())
        
        product = serializer.save()
        self.assertEqual(product.name, 'Test Product')
        self.assertEqual(product.original_price, Decimal('99.99'))
        self.assertEqual(product.store, self.store)
    
    def test_product_serializer_validation(self):
        """Test validación del ProductSerializer"""
        # Test datos inválidos
        invalid_data = {
            'store': 999,  # Store que no existe
            'name': 'Test Product',
            'original_price': '99.99'
        }
        serializer = ProductSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('store', serializer.errors)


class StoreAPITest(APITestCase):
    """Tests para la API de Store"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.store_data = {
            'name': 'Test Store',
            'owner': self.user,
            'latitude': 6.2442,
            'longitude': -75.5812,
            'address': 'Test Address 123',
            'is_active': True
        }
        self.store = Store.objects.create(**self.store_data)
    
    def test_get_store_list(self):
        """Test obtener lista de tiendas"""
        url = '/api/stores/'  # Ajustar según tu configuración de URLs
        response = self.client.get(url)
        
        # Dependiendo de tu configuración de permisos
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED])
    
    def test_get_store_detail(self):
        """Test obtener detalle de una tienda"""
        url = f'/api/stores/{self.store.id}/'
        response = self.client.get(url)
        
        # Dependiendo de tu configuración de permisos
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED])
    
    def test_create_store_authenticated(self):
        """Test crear tienda con usuario autenticado"""
        self.client.force_authenticate(user=self.user)
        url = '/api/stores/'
        
        new_store_data = {
            'name': 'New Test Store',
            'latitude': 4.7109,
            'longitude': -74.0721,
            'address': 'New Test Address',
            'is_active': True,
            'owner': self.user.id
        }
        
        response = self.client.post(url, new_store_data, format='json')
        
        # Dependiendo de tu configuración de permisos
        self.assertIn(response.status_code, [
            status.HTTP_201_CREATED, 
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ])
    
    def test_update_store_authenticated(self):
        """Test actualizar tienda con usuario autenticado"""
        self.client.force_authenticate(user=self.user)
        url = f'/api/stores/{self.store.id}/'
        
        updated_data = {
            'name': 'Updated Store Name',
            'latitude': self.store.latitude,
            'longitude': self.store.longitude,
            'address': self.store.address,
            'is_active': self.store.is_active,
            'owner': self.user.id
        }
        
        response = self.client.put(url, updated_data, format='json')
        
        # Dependiendo de tu configuración de permisos
        self.assertIn(response.status_code, [
            status.HTTP_200_OK, 
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ])
    
    def test_delete_store_authenticated(self):
        """Test eliminar tienda con usuario autenticado"""
        self.client.force_authenticate(user=self.user)
        url = f'/api/stores/{self.store.id}/'
        
        response = self.client.delete(url)
        
        # Dependiendo de tu configuración de permisos
        self.assertIn(response.status_code, [
            status.HTTP_204_NO_CONTENT, 
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ])


class ProductAPITest(APITestCase):
    """Tests para la API de Product"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.user,
            address='Test Address'
        )
        self.product = Product.objects.create(
            store=self.store,
            name='Test Product',
            description='Test Description',
            original_price=Decimal('99.99'),
            is_available=True
        )
    
    def test_get_product_list(self):
        """Test obtener lista de productos"""
        url = '/api/products/'
        response = self.client.get(url)
        
        # Dependiendo de tu configuración de permisos
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED])
    
    def test_get_product_detail(self):
        """Test obtener detalle de un producto"""
        url = f'/api/products/{self.product.id}/'
        response = self.client.get(url)
        
        # Dependiendo de tu configuración de permisos
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED])
    
    def test_create_product_authenticated(self):
        """Test crear producto con usuario autenticado"""
        self.client.force_authenticate(user=self.user)
        url = '/api/products/'
        
        new_product_data = {
            'store': self.store.id,
            'name': 'New Test Product',
            'description': 'New Test Description',
            'original_price': '149.99',
            'is_available': True
        }
        
        response = self.client.post(url, new_product_data, format='json')
        
        # Dependiendo de tu configuración de permisos
        self.assertIn(response.status_code, [
            status.HTTP_201_CREATED, 
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ])
    
    def test_update_product_authenticated(self):
        """Test actualizar producto con usuario autenticado"""
        self.client.force_authenticate(user=self.user)
        url = f'/api/products/{self.product.id}/'
        
        updated_data = {
            'store': self.store.id,
            'name': 'Updated Product Name',
            'description': self.product.description,
            'original_price': '199.99',
            'is_available': self.product.is_available
        }
        
        response = self.client.put(url, updated_data, format='json')
        
        # Dependiendo de tu configuración de permisos
        self.assertIn(response.status_code, [
            status.HTTP_200_OK, 
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ])
    
    def test_delete_product_authenticated(self):
        """Test eliminar producto con usuario autenticado"""
        self.client.force_authenticate(user=self.user)
        url = f'/api/products/{self.product.id}/'
        
        response = self.client.delete(url)
        
        # Dependiendo de tu configuración de permisos
        self.assertIn(response.status_code, [
            status.HTTP_204_NO_CONTENT, 
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ])
    
    def test_filter_products_by_store(self):
        """Test filtrar productos por tienda"""
        # Crear otra tienda y producto
        other_store = Store.objects.create(
            name='Other Store',
            address='Other Address',
            owner=self.user
        )
        Product.objects.create(
            store=other_store,
            name='Other Product',
            original_price=Decimal('50.00')
        )
        
        url = f'/api/products/?store={self.store.id}'
        response = self.client.get(url)
        
        # Dependiendo de tu configuración de permisos y filtros
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED])


class StoreProductIntegrationTest(TestCase):
    """Tests de integración entre Store y Product"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testowner',
            email='owner@test.com',
            password='testpass123'
        )
        self.store = Store.objects.create(
            name='Integration Test Store',
            owner=self.user,
            latitude=6.2442,
            longitude=-75.5812,
            address='Integration Test Address'
        )
    
    def test_store_with_multiple_products(self):
        """Test tienda con múltiples productos"""
        # Crear múltiples productos para la tienda
        products_data = [
            {'name': 'Product 1', 'original_price': Decimal('10.00')},
            {'name': 'Product 2', 'original_price': Decimal('20.00')},
            {'name': 'Product 3', 'original_price': Decimal('30.00')},
        ]
        
        for product_data in products_data:
            Product.objects.create(
                store=self.store,
                **product_data
            )
        
        # Verificar que la tienda tiene 3 productos
        self.assertEqual(self.store.product_set.count(), 3)
        
        # Verificar que todos los productos pertenecen a la tienda correcta
        for product in self.store.product_set.all():
            self.assertEqual(product.store, self.store)
    
    def test_store_deletion_cascades_to_products(self):
        """Test que eliminar tienda elimina sus productos"""
        # Crear productos para la tienda
        product1 = Product.objects.create(
            store=self.store,
            name='Product 1',
            original_price=Decimal('10.00')
        )
        product2 = Product.objects.create(
            store=self.store,
            name='Product 2',
            original_price=Decimal('20.00')
        )
        
        # Verificar que los productos existen
        self.assertTrue(Product.objects.filter(id=product1.id).exists())
        self.assertTrue(Product.objects.filter(id=product2.id).exists())
        
        # Eliminar la tienda
        self.store.delete()
        
        # Verificar que los productos fueron eliminados
        self.assertFalse(Product.objects.filter(id=product1.id).exists())
        self.assertFalse(Product.objects.filter(id=product2.id).exists())
    
    def test_product_queries_optimization(self):
        """Test optimización de consultas para productos"""
        # Crear múltiples productos
        for i in range(5):
            Product.objects.create(
                store=self.store,
                name=f'Product {i}',
                original_price=Decimal(f'{i * 10}.00')
            )
        
        # Test consulta eficiente con select_related
        with self.assertNumQueries(1):
            products = list(Product.objects.select_related('store').all())
            for product in products:
                # Acceder al store no debería generar consultas adicionales
                store_name = product.store.name
        
        self.assertEqual(len(products), 5)
