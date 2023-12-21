from django.db import models
from v1_1.models.user import User


class ServiceRate(models.Model):
    model_name = models.SlugField(unique=True)
    name = models.CharField(max_length=255)
    number_companies = models.IntegerField(default=0)
    number_employees = models.IntegerField(default=0)
    cost = models.FloatField(default=0)

    def __str__(self) -> str:
        return self.model_name


class Subscription(models.Model):
    STATUS = (
        ("process", "Process"),
        ("active", "Active"),
        ("not_active", "No Active"),
        ("pause", "Pause")
    )

    status = models.CharField(max_length=50, default="process", choices=STATUS)
    user = models.ForeignKey('User', models.CASCADE, to_field='username')
    service_rate = models.ForeignKey(ServiceRate, models.CASCADE, to_field='model_name')