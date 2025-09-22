import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace.settings')

app = Celery('marketplace')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check-flash-promos-every-minute': {
        'task': 'promotions.tasks.check_active_promos',
        'schedule': 60.0,
    },
    'cleanup-expired-promos-every-hour': {
        'task': 'promotions.tasks.cleanup_expired_promos',
        'schedule': 3600.0,
    },
    'process-notification-queue-every-30s': {
        'task': 'promotions.tasks.process_notification_queue',
        'schedule': 30.0,
    },
}