# Estructura del Proyecto

## Descripción General

Este documento describe la organización del código, convenciones de nomenclatura y estructura de directorios del proyecto Flash Promos Marketplace.

## Estructura de Directorios

```
flash-promos-marketplace/
├── docs/                          # Documentación del proyecto
├── marketplace/                   # Configuración principal de Django
├── promotions/                    # Módulo de promociones flash
├── stores/                        # Módulo de gestión de tiendas
├── users/                         # Módulo de gestión de usuarios
├── notifications/                 # Módulo de notificaciones
├── terraform/                     # Infraestructura como código
├── scripts/                       # Scripts de utilidad
├── requirements.txt               # Dependencias Python
├── docker-compose.yml             # Configuración de contenedores
├── Dockerfile                     # Imagen de la aplicación
├── .env.example                   # Plantilla de variables de entorno
└── manage.py                      # CLI de Django
```

## Módulos de la Aplicación

### 1. **marketplace/** - Configuración Principal
```
marketplace/
├── __init__.py
├── settings.py                    # Configuración de Django
├── settings_test.py               # Configuración para tests
├── urls.py                        # URLs principales
├── wsgi.py                        # WSGI para producción
├── asgi.py                        # ASGI para WebSockets
├── celery.py                      # Configuración de Celery
└── management/                    # Comandos personalizados de Django
    ├── __init__.py
    └── commands/
```

**Responsabilidades:**
- Configuración global de Django
- URLs principales del proyecto
- Configuración de Celery
- Comandos de gestión personalizados

### 2. **promotions/** - Gestión de Promociones
```
promotions/
├── __init__.py
├── models.py                      # Modelos de promociones
├── views.py                       # Vistas de API
├── serializers.py                 # Serializadores DRF
├── admin.py                       # Configuración del admin
├── apps.py                        # Configuración de la app
├── tasks.py                       # Tareas de Celery
├── tests.py                       # Tests unitarios
├── migrations/                    # Migraciones de base de datos
│   ├── 0001_initial.py
│   ├── 0002_initial.py
│   ├── 0003_initial.py
│   └── __init__.py
└── management/                    # Comandos específicos
    ├── __init__.py
    └── commands/
```

**Responsabilidades:**
- Modelos de promociones flash
- API para gestión de ofertas
- Tareas asíncronas de promociones
- Lógica de negocio de ofertas temporales

### 3. **stores/** - Gestión de Tiendas
```
stores/
├── __init__.py
├── models.py                      # Modelos de tiendas
├── views.py                       # Vistas de API
├── serializers.py                 # Serializadores DRF
├── admin.py                       # Configuración del admin
├── apps.py                        # Configuración de la app
├── tests.py                       # Tests unitarios
├── migrations/                    # Migraciones de base de datos
│   ├── 0001_initial.py
│   ├── 0002_initial.py
│   └── __init__.py
└── management/                    # Comandos específicos
    ├── __init__.py
    └── commands/
```

**Responsabilidades:**
- Modelos de tiendas y comerciantes
- API para gestión de establecimientos
- Información geográfica de tiendas
- Relaciones con promociones

### 4. **users/** - Gestión de Usuarios
```
users/
├── __init__.py
├── models.py                      # Modelos de usuarios
├── views.py                       # Vistas de API
├── serializers.py                 # Serializadores DRF
├── admin.py                       # Configuración del admin
├── apps.py                        # Configuración de la app
├── tests.py                       # Tests unitarios
├── migrations/                    # Migraciones de base de datos
│   ├── 0001_initial.py
│   └── __init__.py
└── management/                    # Comandos específicos
    ├── __init__.py
    └── commands/
```

**Responsabilidades:**
- Modelos de usuarios y perfiles
- Autenticación y autorización
- API de gestión de usuarios
- Preferencias de usuario

### 5. **notifications/** - Sistema de Notificaciones
```
notifications/
├── __init__.py
├── models.py                      # Modelos de notificaciones
├── views.py                       # Vistas de API
├── serializers.py                 # Serializadores DRF
├── utils.py                       # Utilidades de notificación
├── tests.py                       # Tests unitarios
└── migrations/                    # Migraciones de base de datos
    ├── 0001_initial.py
    └── __init__.py
```

**Responsabilidades:**
- Modelos de notificaciones
- Integración con SNS/SQS
- Utilidades de envío de notificaciones
- API de notificaciones

## Infraestructura y Configuración

### **terraform/** - Infraestructura como Código
```
terraform/
├── main.tf                        # Configuración principal
├── variables.tf                   # Variables de Terraform
├── outputs.tf                     # Outputs de infraestructura
├── providers.tf                   # Proveedores (AWS)
├── backend.tf                     # Backend de estado
├── Makefile                       # Comandos de Terraform
├── .terraform.lock.hcl            # Lock de versiones
└── modules/                       # Módulos reutilizables
    └── messaging/                 # Módulo de SNS/SQS
        ├── main.tf
        ├── variables.tf
        └── outputs.tf
```

### **scripts/** - Scripts de Utilidad
```
scripts/
└── init-localstack.sh             # Inicialización de LocalStack
```

### **docs/** - Documentación
```
docs/
├── PROJECT.md                     # Documentación general
├── DOCKER.md                      # Configuración de Docker
├── CELERY.md                      # Configuración de Celery
├── CONFIGURATION.md               # Variables de entorno
├── STRUCTURE.md                   # Este documento
├── TERRAFORM.md                   # Documentación de infraestructura
└── aws-services-diagram.svg       # Diagrama de arquitectura
```

## Convenciones de Código

### Nomenclatura de Archivos
- **Modelos**: `models.py` - Definición de modelos de Django
- **Vistas**: `views.py` - Vistas de API con Django REST Framework
- **Serializadores**: `serializers.py` - Serializadores para API
- **Tareas**: `tasks.py` - Tareas de Celery
- **Tests**: `tests.py` - Tests unitarios
- **Admin**: `admin.py` - Configuración del admin de Django
- **Apps**: `apps.py` - Configuración de la aplicación
- **Utilidades**: `utils.py` - Funciones de utilidad

### Estructura de Modelos
```python
# Ejemplo de estructura de modelo
class PromocionFlash(models.Model):
    """Modelo para promociones flash"""
    
    # Campos principales
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    
    # Campos de tiempo
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'promociones_flash'
        verbose_name = 'Promoción Flash'
        verbose_name_plural = 'Promociones Flash'
    
    def __str__(self):
        return self.titulo
```

### Estructura de Vistas
```python
# Ejemplo de estructura de vista
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

class PromocionFlashViewSet(viewsets.ModelViewSet):
    """ViewSet para promociones flash"""
    
    queryset = PromocionFlash.objects.all()
    serializer_class = PromocionFlashSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtrar promociones activas"""
        return self.queryset.filter(activa=True)
```

### Estructura de Serializadores
```python
# Ejemplo de estructura de serializador
from rest_framework import serializers

class PromocionFlashSerializer(serializers.ModelSerializer):
    """Serializador para promociones flash"""
    
    class Meta:
        model = PromocionFlash
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def validate(self, data):
        """Validación personalizada"""
        if data['fecha_fin'] <= data['fecha_inicio']:
            raise serializers.ValidationError(
                "La fecha de fin debe ser posterior a la fecha de inicio"
            )
        return data
```

## Migraciones de Base de Datos

### Convenciones
- **Numeración**: Secuencial por aplicación (0001, 0002, etc.)
- **Nombres descriptivos**: `0001_initial.py`, `0002_add_user_preferences.py`
- **Dependencias**: Especificar dependencias entre aplicaciones

### Ejemplo de Migración
```python
# migrations/0001_initial.py
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    
    dependencies = [
        ('stores', '0001_initial'),
    ]
    
    operations = [
        migrations.CreateModel(
            name='PromocionFlash',
            fields=[
                ('id', models.BigAutoField(primary_key=True)),
                ('titulo', models.CharField(max_length=200)),
                # ... más campos
            ],
        ),
    ]
```

## Comandos de Gestión

### Ubicación
Cada aplicación puede tener comandos personalizados en:
```
app_name/management/commands/
├── __init__.py
└── comando_personalizado.py
```

### Ejemplo de Comando
```python
# management/commands/check_promos.py
from django.core.management.base import BaseCommand
from promotions.models import PromocionFlash

class Command(BaseCommand):
    help = 'Verifica promociones activas'
    
    def handle(self, *args, **options):
        promos_activas = PromocionFlash.objects.filter(activa=True)
        self.stdout.write(
            self.style.SUCCESS(
                f'Encontradas {promos_activas.count()} promociones activas'
            )
        )
```

## Tests

### Estructura de Tests
```python
# tests.py
from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class PromocionFlashModelTest(TestCase):
    """Tests para el modelo PromocionFlash"""
    
    def setUp(self):
        self.promo = PromocionFlash.objects.create(
            titulo='Test Promo',
            # ... otros campos
        )
    
    def test_str_representation(self):
        self.assertEqual(str(self.promo), 'Test Promo')

class PromocionFlashAPITest(APITestCase):
    """Tests para la API de promociones"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_list_promociones(self):
        response = self.client.get('/api/promociones/')
        self.assertEqual(response.status_code, 200)
```

## Archivos de Configuración

### **requirements.txt**
Dependencias organizadas por categoría:
```txt
# Django Core
Django==4.2.7
djangorestframework==3.14.0

# Base de datos
psycopg2-binary==2.9.9

# Cache y tareas asíncronas
redis==5.0.1
celery==5.3.4

# AWS
boto3==1.34.0
```

### **.env.example**
Plantilla de variables de entorno con valores de ejemplo seguros.

### **.gitignore**
Archivos y directorios excluidos del control de versiones:
```
# Django
*.pyc
__pycache__/
db.sqlite3

# Entorno
.env
venv/

# IDE
.vscode/
.idea/

# Logs
*.log

# Celery
celerybeat-schedule
```

## Scripts de Utilidad

### **Makefile** (raíz del proyecto)
```makefile
# Comandos comunes de desarrollo
.PHONY: help build up down logs shell migrate test

help:
	@echo "Comandos disponibles:"
	@echo "  build    - Construir imágenes"
	@echo "  up       - Iniciar servicios"
	@echo "  down     - Detener servicios"

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

shell:
	docker-compose exec web python manage.py shell

migrate:
	docker-compose exec web python manage.py migrate

test:
	docker-compose exec web python manage.py test
```

## Mejores Prácticas

### Organización de Código
1. **Separación de responsabilidades**: Cada app tiene una responsabilidad específica
2. **Reutilización**: Código común en utilidades compartidas
3. **Modularidad**: Funcionalidades independientes en apps separadas
4. **Documentación**: Docstrings en todas las clases y funciones importantes

### Gestión de Dependencias
1. **Versionado**: Especificar versiones exactas en requirements.txt
2. **Categorización**: Agrupar dependencias por funcionalidad
3. **Actualización**: Revisar y actualizar dependencias regularmente

### Base de Datos
1. **Migraciones**: Crear migraciones descriptivas y atómicas
2. **Índices**: Agregar índices para consultas frecuentes
3. **Constraints**: Usar constraints de base de datos para integridad

### API
1. **Versionado**: Preparar para versionado de API
2. **Documentación**: Usar herramientas como Swagger/OpenAPI
3. **Validación**: Validación robusta en serializadores
4. **Permisos**: Sistema de permisos granular

---

*Esta estructura está diseñada para ser escalable y mantenible, siguiendo las mejores prácticas de Django y desarrollo de APIs.*