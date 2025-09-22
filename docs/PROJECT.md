# Flash Promos Marketplace

## Descripción General

Flash Promos Marketplace es una plataforma de comercio electrónico especializada en promociones flash y ofertas por tiempo limitado. El sistema permite a los comerciantes crear y gestionar promociones temporales mientras proporciona a los usuarios una experiencia de compra optimizada para ofertas de tiempo limitado.

## Arquitectura del Sistema

### Stack Tecnológico

#### Backend
- **Framework**: Django 4.2.7 (Python)
- **Base de Datos**: PostgreSQL con PostGIS (soporte geoespacial)
- **Cache/Message Broker**: Redis
- **Tareas Asíncronas**: Celery
- **API**: Django REST Framework
- **Autenticación**: JWT (djangorestframework-simplejwt)

#### Servicios AWS (LocalStack para desarrollo)
- **SNS**: Notificaciones push y mensajería
- **SQS**: Colas de mensajes para procesamiento asíncrono

#### Infraestructura
- **Contenedores**: Docker y Docker Compose
- **Proxy Reverso**: Nginx (configurado)
- **Orquestación**: Docker Compose para desarrollo
- **IaC**: Terraform para infraestructura AWS

### Arquitectura de Microservicios

El proyecto está organizado en módulos funcionales:

- **Marketplace**: Configuración principal y core del sistema
- **Promotions**: Gestión de promociones flash y ofertas
- **Stores**: Gestión de tiendas y comerciantes
- **Users**: Gestión de usuarios y autenticación
- **Notifications**: Sistema de notificaciones

## Características Principales

### Funcionalidades Core
- Gestión de promociones flash con tiempo limitado
- Sistema de notificaciones en tiempo real
- Geolocalización para ofertas basadas en ubicación
- Procesamiento asíncrono de tareas
- API RESTful completa
- Autenticación JWT segura

### Procesamiento Asíncrono
El sistema utiliza Celery para tareas programadas:
- Verificación de promociones activas (cada minuto)
- Limpieza de promociones expiradas (cada hora)
- Procesamiento de cola de notificaciones (cada 30 segundos)

### Seguridad
- Autenticación JWT con refresh tokens
- CORS configurado para frontend
- Variables de entorno para configuración sensible
- Validación de datos con Django REST Framework

## Entornos

### Desarrollo
- **Base de Datos**: PostgreSQL en Docker
- **AWS Services**: LocalStack (emulación local)
- **Cache**: Redis en Docker
- **Hot Reload**: Habilitado para desarrollo

### Configuración de Variables
El sistema utiliza variables de entorno para configuración:
- Configuración de base de datos
- Credenciales AWS
- Configuración de Redis/Celery
- Configuración de Django (DEBUG, SECRET_KEY)

## Dependencias Principales

### Backend Core
```
Django==4.2.7
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.0
django-cors-headers==4.3.1
```

### Base de Datos y Cache
```
psycopg2-binary==2.9.9
django-redis==5.4.0
redis==5.0.1
```

### Tareas Asíncronas
```
celery==5.3.4
django-celery-beat==2.5.0
django-celery-results==2.5.0
```

### AWS y Cloud
```
boto3==1.34.0
localstack-client==2.5
```

### Geolocalización
```
django-location-field==2.7.3
```

## Flujo de Trabajo

### Desarrollo Local
1. Configurar variables de entorno (`.env`)
2. Ejecutar `docker-compose up` para servicios
3. Aplicar migraciones de base de datos
4. Iniciar servidor de desarrollo
5. Iniciar worker de Celery para tareas asíncronas

### Despliegue
1. Provisionar infraestructura con Terraform
2. Configurar variables de entorno de producción
3. Construir y desplegar contenedores
4. Aplicar migraciones de base de datos
5. Configurar servicios de monitoreo

## Monitoreo y Logging

- **Logging**: Configurado en Django settings
- **Health Checks**: Implementados en Docker Compose
- **Métricas**: Celery monitoring disponible

---

*Para más detalles técnicos, consultar la documentación específica de cada componente en esta carpeta.*