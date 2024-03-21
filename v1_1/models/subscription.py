from django.db import models
from datetime import timedelta
from django.utils import timezone
from datetime import datetime, time
from celery import shared_task
from celery.schedules import crontab
from migration_control_web.celery import app
from celery import Celery


class ServiceRate(models.Model):
    TYPES_TARIFFS = (
        ('standard', 'Стандартная'),
        ('pro', 'Про'),
    )

    type_tariff = models.SlugField('Тип тарифа', choices=TYPES_TARIFFS, unique=True)
    name = models.CharField('Название', max_length=255)
    cost_organizations = models.FloatField('Цена за организацию', default=0)
    cost_workers = models.FloatField('Цена за сотрудника', default=0)
    cost_all_documents = models.FloatField('Цена за расширенный пакет', default=0)

    class Meta:
        verbose_name = 'Тарифная ставка'
        verbose_name_plural = 'Тарифные ставки'

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

        # Если пользователь поменял другие данные, допустим кол-во работников, но при этом у него поле status и так уже
        # имеет значение "active", то не должно быть повторного вычисления этих дат, они должны остаться без изменения
        if self.status == 'active' and not self.start_date:
            # Если в подписке пользователя выбирается статус `active`, то вычисляется текущая дата для поля start_date
            # и вычисляется дата (текущая дата + 30 дней) для поля expiration_date.
            self.start_date = datetime.now().date()
            self.expiration_date = self.start_date + timedelta(days=30)

            if self.service_rate.type_tariff == 'pro':
                # Запись платежа за расширенный пакет в историю
                HistoryPayment.objects.create(
                    user=owner,
                    operation='Расширенный пакет',
                    amount=self.service_rate.cost_all_documents
                )
        elif self.status == 'not_active' and self.start_date:
            # Если в подписке пользователя выбирается статус `not_active`, то обнуляется дата для поля start_date и
            # expiration_date.
            self.start_date = None
            self.expiration_date = None

        super(Subscription, self).save(*args, **kwargs)


@shared_task
def checking_subscription_relevance():
    subscriptions = Subscription.objects.all()
    for subscription in subscriptions:
        if subscription.status == 'active':
            current_datetime = timezone.now()
            expiration_date = timezone.make_aware(datetime.combine(subscription.expiration_date, time(hour=23)))

            if subscription.status == 'active' and (current_datetime >= expiration_date):
                subscription.status = 'not_active'
                subscription.save()

