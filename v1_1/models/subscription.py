from datetime import datetime
from django.db import models
from v1_1.models.user import User


class ServiceRate(models.Model):
    TYPES_TARIFFS = (
        ('standard', 'Стандартная'),
        ('pro', 'Про'),
    )

    type_tariff = models.SlugField(choices=TYPES_TARIFFS, unique=True)
    name = models.CharField(max_length=255)
    cost_organizations = models.FloatField(default=0)
    cost_workers = models.FloatField(default=0)
    cost_all_documents = models.FloatField(default=0)

    def __str__(self) -> str:
        return self.model_name


class Subscription(models.Model):
    STATUS = (
        ('process', 'Process'),
        ('active', 'Active'),
        ('not_active', 'No Active'),
        ('pause', 'Pause')
    )

    status = models.CharField(max_length=50, default='process', choices=STATUS)
    user = models.ForeignKey('User', models.CASCADE, to_field='username', unique=True)
    service_rate = models.ForeignKey(ServiceRate, models.CASCADE, to_field='type_tariff')
    number_organizations = models.IntegerField(default=0)
    number_workers = models.IntegerField(default=0)
    expiration_date = models.DateField()
    all_documents = models.BooleanField(default=False, null=True)