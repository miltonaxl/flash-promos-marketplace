from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models as gis_models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('new', 'New User'),
        ('frequent', 'Frequent Buyer'),
        ('regular', 'Regular User'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='regular')
    location = gis_models.PointField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    notification_preferences = models.JSONField(default=dict)
    last_notification_sent = models.DateField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.username