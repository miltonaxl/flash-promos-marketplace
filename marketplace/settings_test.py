"""Test settings for marketplace project."""

import os
from .settings import *

# Override database configuration for tests
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('POSTGRES_DB', 'test_marketplace'),
        'USER': os.getenv('POSTGRES_USER', 'marketplace'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'password'),
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
        'TEST': {
            'NAME': 'test_marketplace',
        },
    }
}

# Enable GIS support for tests
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',  # Enable GIS for tests
    
    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_celery_beat',
    'django_filters',
    
    # Local apps
    'marketplace',
    'promotions',
    'stores',
    'users',
    'notifications',
]

# GDAL configuration for tests
import os
GDAL_LIBRARY_PATH = os.environ.get('GDAL_LIBRARY_PATH', None)
GEOS_LIBRARY_PATH = os.environ.get('GEOS_LIBRARY_PATH', None)



# Test-specific settings
DEBUG = True
TEST = True

# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Celery settings for tests - execute tasks synchronously
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATION = True
CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'cache+memory://'

# AWS settings for tests - disable external services
AWS_SNS_ENDPOINT_URL = None
AWS_SQS_ENDPOINT_URL = None
FLASH_PROMO_TOPIC_ARN = None

# Fast password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable caching for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Email backend for tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Logging configuration for tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'ERROR',
    },
}

# Security settings disabled for tests
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False