# Configuración de Docker

## Descripción General

El proyecto utiliza Docker y Docker Compose para crear un entorno de desarrollo consistente y reproducible. La configuración incluye todos los servicios necesarios para ejecutar la aplicación completa localmente.

## Arquitectura de Contenedores

### Servicios Principales

#### 1. **web** - Aplicación Django
- **Imagen**: Construida desde Dockerfile local
- **Puerto**: 8000:8000
- **Comando**: Ejecuta migraciones y servidor de desarrollo
- **Volúmenes**: Código fuente montado para hot reload

#### 2. **celery** - Worker de Tareas Asíncronas
- **Imagen**: Construida desde Dockerfile local
- **Comando**: `celery -A marketplace worker --loglevel=info`
- **Función**: Procesa tareas en background

#### 3. **celery-beat** - Programador de Tareas
- **Imagen**: Construida desde Dockerfile local
- **Comando**: `celery -A marketplace beat --loglevel=info`
- **Función**: Ejecuta tareas programadas (cron jobs)

### Servicios de Infraestructura

#### 4. **postgres** - Base de Datos
- **Imagen**: `postgis/postgis:15-3.3`
- **Puerto**: 5432:5432
- **Características**: PostgreSQL con extensión PostGIS para datos geoespaciales
- **Volumen**: `postgres_data` para persistencia
- **Health Check**: Verificación de disponibilidad

#### 5. **redis** - Cache y Message Broker
- **Imagen**: `redis:alpine`
- **Puerto**: 6379:6379
- **Función**: Cache de Django y broker para Celery

#### 6. **localstack** - Emulación de AWS
- **Imagen**: `localstack/localstack:latest`
- **Puerto**: 4566:4566
- **Servicios**: SNS, SQS
- **Función**: Emula servicios AWS para desarrollo local

## Dockerfile

### Configuración Base
```dockerfile
FROM python:3.11-slim
```

### Dependencias del Sistema
- **gcc**: Compilador para dependencias nativas
- **libpq-dev**: Cliente PostgreSQL
- **PostGIS**: Bibliotecas geoespaciales
  - binutils
  - libproj-dev
  - gdal-bin
  - libgdal-dev
  - python3-gdal

### Configuración de Seguridad
- Usuario no-root (`app`) para ejecutar la aplicación
- Ownership correcto de archivos
- Exposición mínima de puertos

### Optimizaciones
- Cache de dependencias Python mediante copia separada de `requirements.txt`
- Limpieza de cache de apt para reducir tamaño de imagen
- Uso de `--no-cache-dir` para pip

## Docker Compose

### Red
```yaml
networks:
  app-network:
    driver: bridge
```
Todos los servicios se comunican a través de una red bridge personalizada.

### Volúmenes
```yaml
volumes:
  postgres_data:
```
Persistencia de datos de PostgreSQL entre reinicios.

### Variables de Entorno
Todos los servicios comparten las mismas variables de entorno:

#### Django/Aplicación
- `DEBUG`: Modo debug
- `SECRET_KEY`: Clave secreta de Django

#### Base de Datos
- `POSTGRES_DB`: Nombre de la base de datos
- `POSTGRES_USER`: Usuario de PostgreSQL
- `POSTGRES_PASSWORD`: Contraseña de PostgreSQL
- `POSTGRES_HOST`: Host de la base de datos (postgres)
- `POSTGRES_PORT`: Puerto de la base de datos (5432)

#### Redis/Celery
- `REDIS_URL`: URL de conexión a Redis
- `CELERY_BROKER_URL`: Broker para Celery
- `CELERY_RESULT_BACKEND`: Backend de resultados

#### AWS/LocalStack
- `AWS_ACCESS_KEY_ID`: Credenciales AWS
- `AWS_SECRET_ACCESS_KEY`: Credenciales AWS
- `AWS_DEFAULT_REGION`: Región por defecto
- `AWS_SNS_ENDPOINT_URL`: Endpoint de SNS (LocalStack)
- `AWS_SQS_ENDPOINT_URL`: Endpoint de SQS (LocalStack)
- `FLASH_PROMO_TOPIC_ARN`: ARN del tópico SNS

### Dependencias entre Servicios

#### Servicio Web
```yaml
depends_on:
  postgres:
    condition: service_healthy
  redis:
    condition: service_started
  localstack:
    condition: service_started
```

#### Servicios Celery
```yaml
depends_on:
  - postgres
  - redis
  - localstack
```

## Comandos de Uso

### Desarrollo Local

#### Iniciar todos los servicios
```bash
docker-compose up
```

#### Iniciar en background
```bash
docker-compose up -d
```

#### Ver logs
```bash
docker-compose logs -f [servicio]
```

#### Detener servicios
```bash
docker-compose down
```

#### Reconstruir imágenes
```bash
docker-compose build
```

#### Ejecutar comandos en contenedores
```bash
# Shell en el contenedor web
docker-compose exec web bash

# Ejecutar migraciones
docker-compose exec web python manage.py migrate

# Crear superusuario
docker-compose exec web python manage.py createsuperuser
```

### Gestión de Datos

#### Backup de base de datos
```bash
docker-compose exec postgres pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup.sql
```

#### Restaurar base de datos
```bash
docker-compose exec -T postgres psql -U $POSTGRES_USER $POSTGRES_DB < backup.sql
```

#### Limpiar volúmenes
```bash
docker-compose down -v
```

## Health Checks

### PostgreSQL
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
  interval: 10s
  timeout: 5s
  retries: 5
```

## Troubleshooting

### Problemas Comunes

#### Puerto ya en uso
```bash
# Verificar puertos en uso
lsof -i :8000
lsof -i :5432
lsof -i :6379
```

#### Problemas de permisos
```bash
# Reconstruir con permisos correctos
docker-compose build --no-cache
```

#### Base de datos no disponible
```bash
# Verificar health check
docker-compose ps

# Ver logs de PostgreSQL
docker-compose logs postgres
```

#### Problemas de red
```bash
# Recrear red
docker-compose down
docker network prune
docker-compose up
```

### Logs y Debugging

#### Ver logs de todos los servicios
```bash
docker-compose logs
```

#### Logs específicos
```bash
docker-compose logs web
docker-compose logs celery
docker-compose logs postgres
```

#### Modo debug
```bash
# Ejecutar con variables de debug
DEBUG=True docker-compose up
```

## Optimizaciones de Producción

### Consideraciones
- Usar imágenes multi-stage para reducir tamaño
- Configurar límites de recursos
- Implementar health checks para todos los servicios
- Usar secrets para variables sensibles
- Configurar logging centralizado
- Implementar monitoring y métricas

### Ejemplo de Configuración de Producción
```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

---

*Para más información sobre configuración específica, consultar `.env.example` y la documentación de configuración.*