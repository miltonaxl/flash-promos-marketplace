# Configuración de Celery

## Descripción General

Celery es el sistema de tareas asíncronas utilizado en Flash Promos Marketplace para manejar operaciones en background y tareas programadas. Permite procesar tareas de manera asíncrona sin bloquear las respuestas HTTP y ejecutar tareas recurrentes de manera automática.

## Arquitectura de Celery

### Componentes

#### 1. **Celery Worker**
- **Función**: Procesa tareas asíncronas en background
- **Comando**: `celery -A marketplace worker --loglevel=info`
- **Contenedor**: `celery` en Docker Compose

#### 2. **Celery Beat**
- **Función**: Programador de tareas (cron scheduler)
- **Comando**: `celery -A marketplace beat --loglevel=info`
- **Contenedor**: `celery-beat` en Docker Compose

#### 3. **Message Broker**
- **Servicio**: Redis
- **URL**: `redis://redis:6379/0`
- **Función**: Cola de mensajes entre Django y workers

#### 4. **Result Backend**
- **Servicio**: Redis
- **URL**: `redis://redis:6379/0`
- **Función**: Almacena resultados de tareas ejecutadas

## Configuración

### Archivo de Configuración (`marketplace/celery.py`)

```python
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace.settings')

app = Celery('marketplace')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

### Variables de Entorno

#### Configuración de Broker y Backend
```bash
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

#### Configuración en Django Settings
```python
# Configuración automática desde variables de entorno
# Namespace 'CELERY' permite usar CELERY_* en variables de entorno
```

## Tareas Programadas (Beat Schedule)

### 1. **Verificación de Promociones Activas**
```python
'check-flash-promos-every-minute': {
    'task': 'promotions.tasks.check_active_promos',
    'schedule': 60.0,  # Cada 60 segundos
}
```
- **Frecuencia**: Cada minuto
- **Función**: Verifica y actualiza el estado de promociones flash
- **Importancia**: Crítica para la funcionalidad principal

### 2. **Limpieza de Promociones Expiradas**
```python
'cleanup-expired-promos-every-hour': {
    'task': 'promotions.tasks.cleanup_expired_promos',
    'schedule': 3600.0,  # Cada 3600 segundos (1 hora)
}
```
- **Frecuencia**: Cada hora
- **Función**: Limpia promociones expiradas de la base de datos
- **Importancia**: Mantenimiento y optimización

### 3. **Procesamiento de Cola de Notificaciones**
```python
'process-notification-queue-every-30s': {
    'task': 'promotions.tasks.process_notification_queue',
    'schedule': 30.0,  # Cada 30 segundos
}
```
- **Frecuencia**: Cada 30 segundos
- **Función**: Procesa notificaciones pendientes
- **Importancia**: Experiencia de usuario en tiempo real

## Configuración de Docker

### Worker Container
```yaml
celery:
  build: .
  command: celery -A marketplace worker --loglevel=info
  volumes:
    - .:/app
  environment:
    - CELERY_BROKER_URL=redis://redis:6379/0
    - CELERY_RESULT_BACKEND=redis://redis:6379/0
    # ... otras variables de entorno
  depends_on:
    - postgres
    - redis
    - localstack
```

### Beat Container
```yaml
celery-beat:
  build: .
  command: celery -A marketplace beat --loglevel=info
  volumes:
    - .:/app
  environment:
    - CELERY_BROKER_URL=redis://redis:6379/0
    - CELERY_RESULT_BACKEND=redis://redis:6379/0
    # ... otras variables de entorno
  depends_on:
    - postgres
    - redis
    - localstack
```

## Comandos de Gestión

### Desarrollo Local

#### Iniciar Worker
```bash
# Dentro del contenedor
celery -A marketplace worker --loglevel=info

# Con Docker Compose
docker-compose up celery
```

#### Iniciar Beat Scheduler
```bash
# Dentro del contenedor
celery -A marketplace beat --loglevel=info

# Con Docker Compose
docker-compose up celery-beat
```

#### Monitoreo
```bash
# Ver workers activos
celery -A marketplace inspect active

# Ver tareas programadas
celery -A marketplace inspect scheduled

# Ver estadísticas
celery -A marketplace inspect stats
```

### Comandos de Debugging

#### Ejecutar Tarea Manualmente
```bash
# Desde Django shell
python manage.py shell
>>> from promotions.tasks import check_active_promos
>>> result = check_active_promos.delay()
>>> result.get()
```

#### Ver Logs
```bash
# Logs del worker
docker-compose logs celery

# Logs del beat scheduler
docker-compose logs celery-beat

# Logs en tiempo real
docker-compose logs -f celery
```

## Estructura de Tareas

### Ubicación de Tareas
```
promotions/
├── tasks.py              # Tareas relacionadas con promociones
│   ├── check_active_promos
│   ├── cleanup_expired_promos
│   └── process_notification_queue
```

### Ejemplo de Tarea
```python
from celery import shared_task
from django.utils import timezone

@shared_task
def check_active_promos():
    """Verifica y actualiza promociones activas"""
    # Lógica de la tarea
    pass
```

## Monitoreo y Métricas

### Flower (Opcional)
Para monitoreo web de Celery:
```bash
# Instalar Flower
pip install flower

# Ejecutar
celery -A marketplace flower
```

### Métricas Importantes
- **Tareas procesadas por minuto**
- **Tiempo promedio de ejecución**
- **Tareas fallidas**
- **Workers activos**
- **Cola de tareas pendientes**

## Configuración de Producción

### Optimizaciones
```python
# En settings.py
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
```

### Configuración de Logging
```python
CELERY_WORKER_LOG_FORMAT = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
CELERY_WORKER_TASK_LOG_FORMAT = '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s'
```

### Configuración de Retry
```python
@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def robust_task(self):
    # Tarea con reintentos automáticos
    pass
```

## Troubleshooting

### Problemas Comunes

#### Worker no se conecta a Redis
```bash
# Verificar conexión a Redis
docker-compose exec redis redis-cli ping

# Verificar configuración de URL
echo $CELERY_BROKER_URL
```

#### Tareas no se ejecutan
```bash
# Verificar que Beat esté ejecutándose
docker-compose ps celery-beat

# Verificar logs de Beat
docker-compose logs celery-beat
```

#### Tareas se acumulan
```bash
# Verificar workers activos
celery -A marketplace inspect active

# Purgar cola
celery -A marketplace purge
```

### Debugging

#### Ejecutar Worker en Modo Debug
```bash
celery -A marketplace worker --loglevel=debug
```

#### Verificar Configuración
```bash
celery -A marketplace inspect conf
```

#### Reiniciar Workers
```bash
# Reinicio suave
celery -A marketplace control pool_restart

# Reinicio completo
docker-compose restart celery celery-beat
```

## Mejores Prácticas

### Diseño de Tareas
1. **Idempotencia**: Las tareas deben poder ejecutarse múltiples veces sin efectos secundarios
2. **Atomicidad**: Cada tarea debe ser una unidad de trabajo completa
3. **Timeout**: Configurar timeouts apropiados para evitar tareas colgadas
4. **Logging**: Incluir logging detallado para debugging

### Gestión de Errores
1. **Retry Logic**: Implementar reintentos para errores transitorios
2. **Dead Letter Queue**: Manejar tareas que fallan repetidamente
3. **Alertas**: Configurar alertas para fallos críticos

### Performance
1. **Concurrencia**: Ajustar número de workers según recursos
2. **Prefetch**: Configurar prefetch multiplier apropiado
3. **Particionamiento**: Dividir tareas grandes en subtareas

---

*Para más información sobre tareas específicas, consultar el código en los módulos correspondientes.*