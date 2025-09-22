# Configuración de Entorno

## Descripción General

Este documento describe todas las variables de entorno y configuraciones necesarias para ejecutar Flash Promos Marketplace en diferentes entornos (desarrollo, staging, producción).

## Variables de Entorno

### Configuración de Django

#### Variables Principales
```bash
# Modo debug (solo desarrollo)
DEBUG=True

# Clave secreta de Django (CRÍTICO: cambiar en producción)
SECRET_KEY=your-secret-key-here

# Hosts permitidos (separados por coma)
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
```

**Consideraciones de Seguridad:**
- `SECRET_KEY` debe ser única y segura en producción
- `DEBUG` debe ser `False` en producción
- `ALLOWED_HOSTS` debe incluir solo dominios autorizados

### Configuración de Base de Datos

#### PostgreSQL
```bash
# Configuración de base de datos
POSTGRES_DB=flash_promos_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

**Notas:**
- En Docker Compose, `POSTGRES_HOST=postgres` (nombre del servicio)
- Para producción, usar credenciales seguras
- La base de datos incluye extensión PostGIS para datos geoespaciales

### Configuración de Redis

#### Cache y Message Broker
```bash
# URL de conexión a Redis
REDIS_URL=redis://localhost:6379/0

# Configuración específica de Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

**Uso:**
- Cache de Django
- Message broker para Celery
- Almacenamiento de resultados de tareas

### Configuración de AWS

#### Credenciales
```bash
# Credenciales de AWS (para LocalStack en desarrollo)
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_DEFAULT_REGION=us-east-1
```

#### Endpoints de Servicios
```bash
# URLs de servicios AWS (LocalStack para desarrollo)
AWS_SNS_ENDPOINT_URL=http://localhost:4566
AWS_SQS_ENDPOINT_URL=http://localhost:4566

# ARN del tópico SNS para promociones flash
FLASH_PROMO_TOPIC_ARN=arn:aws:sns:us-east-1:000000000000:flash-promos
```

**Entornos:**
- **Desarrollo**: LocalStack (endpoints locales)
- **Producción**: Servicios AWS reales (sin endpoints)

## Configuración por Entorno

### Desarrollo Local

#### Archivo `.env`
```bash
# Django
DEBUG=True
SECRET_KEY=dev-secret-key-not-for-production
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Base de datos (Docker)
POSTGRES_DB=flash_promos_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis (Docker)
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# AWS LocalStack
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_DEFAULT_REGION=us-east-1
AWS_SNS_ENDPOINT_URL=http://localstack:4566
AWS_SQS_ENDPOINT_URL=http://localstack:4566
FLASH_PROMO_TOPIC_ARN=arn:aws:sns:us-east-1:000000000000:flash-promos
```

### Staging

#### Configuración de Staging
```bash
# Django
DEBUG=False
SECRET_KEY=staging-secret-key-secure
ALLOWED_HOSTS=staging.flashpromos.com

# Base de datos (RDS)
POSTGRES_DB=flash_promos_staging
POSTGRES_USER=staging_user
POSTGRES_PASSWORD=secure_staging_password
POSTGRES_HOST=staging-db.region.rds.amazonaws.com
POSTGRES_PORT=5432

# Redis (ElastiCache)
REDIS_URL=redis://staging-redis.region.cache.amazonaws.com:6379/0
CELERY_BROKER_URL=redis://staging-redis.region.cache.amazonaws.com:6379/0
CELERY_RESULT_BACKEND=redis://staging-redis.region.cache.amazonaws.com:6379/0

# AWS (servicios reales)
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-east-1
# Sin endpoints (usa servicios AWS reales)
FLASH_PROMO_TOPIC_ARN=arn:aws:sns:us-east-1:123456789012:flash-promos-staging
```

### Producción

#### Configuración de Producción
```bash
# Django
DEBUG=False
SECRET_KEY=production-secret-key-very-secure
ALLOWED_HOSTS=flashpromos.com,www.flashpromos.com

# Base de datos (RDS Multi-AZ)
POSTGRES_DB=flash_promos_prod
POSTGRES_USER=prod_user
POSTGRES_PASSWORD=very_secure_production_password
POSTGRES_HOST=prod-db.region.rds.amazonaws.com
POSTGRES_PORT=5432

# Redis (ElastiCache Cluster)
REDIS_URL=redis://prod-redis.region.cache.amazonaws.com:6379/0
CELERY_BROKER_URL=redis://prod-redis.region.cache.amazonaws.com:6379/0
CELERY_RESULT_BACKEND=redis://prod-redis.region.cache.amazonaws.com:6379/0

# AWS (servicios reales con IAM roles)
AWS_DEFAULT_REGION=us-east-1
# Usar IAM roles en lugar de credenciales hardcoded
FLASH_PROMO_TOPIC_ARN=arn:aws:sns:us-east-1:123456789012:flash-promos-prod
```

## Configuración en Django Settings

### Lectura de Variables de Entorno
```python
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Django core settings
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-key-for-dev')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('POSTGRES_DB', 'flash_promos_db'),
        'USER': os.getenv('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'postgres'),
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}

# Redis configuration
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Celery configuration
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', REDIS_URL)

# AWS configuration
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
```

## Gestión de Secretos

### Desarrollo
- Usar archivo `.env` (incluido en `.gitignore`)
- Copiar desde `.env.example` y modificar valores

### Staging/Producción
- **AWS Secrets Manager**: Para credenciales de base de datos
- **AWS Parameter Store**: Para configuración de aplicación
- **IAM Roles**: Para credenciales AWS
- **Variables de entorno del contenedor**: Para configuración específica

### Ejemplo con AWS Secrets Manager
```python
import boto3
import json

def get_secret(secret_name, region_name):
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        secret = get_secret_value_response['SecretString']
        return json.loads(secret)
    except Exception as e:
        raise e

# Uso en settings.py
if not DEBUG:
    db_secrets = get_secret('prod/database', AWS_DEFAULT_REGION)
    DATABASES['default']['PASSWORD'] = db_secrets['password']
```

## Validación de Configuración

### Script de Validación
```python
#!/usr/bin/env python
"""Script para validar configuración de entorno"""

import os
import sys

REQUIRED_VARS = [
    'SECRET_KEY',
    'POSTGRES_DB',
    'POSTGRES_USER',
    'POSTGRES_PASSWORD',
    'REDIS_URL',
    'AWS_DEFAULT_REGION',
]

PRODUCTION_VARS = [
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'FLASH_PROMO_TOPIC_ARN',
]

def validate_config():
    missing_vars = []
    
    # Verificar variables requeridas
    for var in REQUIRED_VARS:
        if not os.getenv(var):
            missing_vars.append(var)
    
    # Verificar variables de producción si DEBUG=False
    if os.getenv('DEBUG', 'False').lower() == 'false':
        for var in PRODUCTION_VARS:
            if not os.getenv(var):
                missing_vars.append(var)
    
    if missing_vars:
        print(f"Error: Variables de entorno faltantes: {missing_vars}")
        sys.exit(1)
    
    print("✓ Configuración válida")

if __name__ == '__main__':
    validate_config()
```

## Troubleshooting

### Problemas Comunes

#### Variables no cargadas
```bash
# Verificar que el archivo .env existe
ls -la .env

# Verificar contenido
cat .env

# Verificar variables en el contenedor
docker-compose exec web env | grep POSTGRES
```

#### Conexión a base de datos
```bash
# Probar conexión desde contenedor
docker-compose exec web python manage.py dbshell

# Verificar configuración
docker-compose exec web python manage.py check --database default
```

#### Conexión a Redis
```bash
# Probar conexión
docker-compose exec redis redis-cli ping

# Verificar desde Django
docker-compose exec web python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value')
>>> cache.get('test')
```

### Debugging

#### Ver todas las variables de entorno
```bash
# En el contenedor
docker-compose exec web env

# Filtrar por prefijo
docker-compose exec web env | grep POSTGRES
docker-compose exec web env | grep AWS
```

#### Verificar configuración de Django
```python
# En Django shell
python manage.py shell
>>> from django.conf import settings
>>> settings.DEBUG
>>> settings.DATABASES
>>> settings.CELERY_BROKER_URL
```

## Mejores Prácticas

### Seguridad
1. **Nunca** commitear archivos `.env` al repositorio
2. Usar secretos seguros en producción
3. Rotar credenciales regularmente
4. Usar IAM roles en lugar de credenciales hardcoded
5. Validar configuración en startup

### Gestión
1. Documentar todas las variables requeridas
2. Proporcionar valores por defecto seguros para desarrollo
3. Usar herramientas de gestión de secretos en producción
4. Implementar validación de configuración
5. Monitorear acceso a secretos

### Desarrollo
1. Mantener `.env.example` actualizado
2. Usar valores de desarrollo seguros
3. Documentar diferencias entre entornos
4. Automatizar validación de configuración

---

*Para configurar un nuevo entorno, copiar `.env.example` a `.env` y modificar los valores según el entorno objetivo.*