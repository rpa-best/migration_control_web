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

    def __str__(self):
        return self.get_type_tariff_display()


class Subscription(models.Model):
    STATUS = (
        ('process', 'В процессе'),
        ('active', 'Активная'),
        ('not_active', 'Не активная'),
        ('pause', 'Пауза')
    )

    status = models.CharField('Статус', max_length=50, default='process', choices=STATUS)
    user = models.OneToOneField('User', verbose_name='Пользователь', on_delete=models.CASCADE, to_field='username')
    service_rate = models.ForeignKey(ServiceRate, verbose_name='Тариф', on_delete=models.CASCADE,
                                     to_field='type_tariff')
    number_organizations = models.IntegerField('Количество организаций', default=1)
    number_workers = models.IntegerField('Количество работников', default=10)
    default_cost = models.FloatField('Стоимость по умолчанию', blank=True, null=True)
    start_date = models.DateField('Дата начала', blank=True, null=True)
    expiration_date = models.DateField('Дата окончания', blank=True, null=True)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'