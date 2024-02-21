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
    cost = models.FloatField('Стоимость', blank=True, null=True)
    start_date = models.DateField('Дата начала', blank=True, null=True)
    expiration_date = models.DateField('Дата окончания', blank=True, null=True)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def save(self, *args, **kwargs):
        # Вычисление цены при подачах заявки за подписку с указанными параметрами и тарифом
        # Если пользователь в подписке выбрал тариф 'standard', то поле cost_all_documents для вычисления не
        # используется, поскольку только при тарифе pro(Про) указывается сумма для поля cost_all_documents
        if self.service_rate.type_tariff == 'standard':
            self.cost = (self.number_organizations * self.service_rate.cost_organizations) + (
                        self.number_workers * self.service_rate.cost_workers)
        elif self.service_rate.type_tariff == 'pro':
            self.cost = (self.number_organizations * self.service_rate.cost_organizations) + (
                        self.number_workers * self.service_rate.cost_workers) + self.service_rate.cost_all_documents

        super(Subscription, self).save(*args, **kwargs)

    # Вычисление цены при изменении заявки за подписку с указанными параметрами и тарифом
    def update(self, *args, **kwargs):
        if self.service_rate.type_tariff == 'standard':
            self.cost = (self.number_organizations * self.service_rate.cost_organizations) + (
                        self.number_workers * self.service_rate.cost_workers)
        elif self.service_rate.type_tariff == 'pro':
            self.cost = (self.number_organizations * self.service_rate.cost_organizations) + (
                        self.number_workers * self.service_rate.cost_workers) + self.service_rate.cost_all_documents

        super(Subscription, self).save(*args, **kwargs)