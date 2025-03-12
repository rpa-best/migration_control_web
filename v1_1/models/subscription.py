from django.db import models
from django.utils import timezone
from datetime import datetime, time
from celery import shared_task
from .user import HistoryPayment, User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class Benefits(models.Model):
    name = models.CharField('Название', max_length=255, unique=True)

    class Meta:
        verbose_name = 'Выгода'
        verbose_name_plural = 'Выгоды'

    def __str__(self):
        return self.name


class ServiceRate(models.Model):
    TYPES_TARIFFS = (
        ('standard', 'Стандартная'),
        ('pro', 'Про'),
    )

    type_tariff = models.CharField('Тип тарифа', choices=TYPES_TARIFFS, unique=True)
    name = models.CharField('Название', max_length=255)
    description = models.TextField('Описание')
    number_organizations = models.IntegerField('Количество организаций', default=1)
    number_workers = models.IntegerField('Количество работников', default=10)
    price = models.FloatField('Цена', default=0)
    cost_organizations = models.FloatField('Цена за организацию', default=0)
    cost_workers = models.FloatField('Цена за сотрудника', default=0)

    class Meta:
        verbose_name = 'Тарифная ставка'
        verbose_name_plural = 'Тарифные ставки'

    def __str__(self):
        return self.get_type_tariff_display()


class BenefitsServiceRate(models.Model):
    service_rate = models.ForeignKey(ServiceRate, on_delete=models.CASCADE, verbose_name='Тариф', related_name='benefitsservicerate_set')
    benefit = models.ForeignKey(Benefits, verbose_name='Выгода', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name = 'Выгода тарифа'
        verbose_name_plural = 'Выгоды тарифа'
        unique_together = ('service_rate', 'benefit')


class Subscription(models.Model):
    STATUS = (
        ('process', 'В процессе'),
        ('active', 'Активная'),
        ('not_active', 'Не активная'),
        ('pause', 'Пауза')
    )

    status = models.CharField('Статус', max_length=50, default='process', choices=STATUS)
    user = models.OneToOneField('User', verbose_name='Пользователь', on_delete=models.CASCADE, to_field='username')
    # service_rate = models.ForeignKey(ServiceRate, verbose_name='Тариф', on_delete=models.CASCADE,
    #                                  to_field='type_tariff')
    service_rate = models.ForeignKey(ServiceRate, verbose_name='Тариф', on_delete=models.CASCADE)
    start_date = models.DateField('Дата начала', blank=True, null=True)
    expiration_date = models.DateField('Дата окончания', blank=True, null=True)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def save(self, *args, **kwargs):
        if self.status == 'active':
            # Проверка на достаточность средств
            if self.user.balance < self.service_rate.price:
                raise ValidationError(
                    _('У пользователя недостаточно денежных средств на балансе для одобрения подписки'))

            if self.service_rate.type_tariff == 'standard':
                HistoryPayment.objects.create(
                    user=self.user,
                    operation='Покупка стандартной подписки',
                    amount=self.service_rate.price
                )
            elif self.service_rate.type_tariff == 'pro':
                # Запись платежа за расширенный пакет в историю
                HistoryPayment.objects.create(
                    user=self.user,
                    operation='Покупка про подписки',
                    amount=self.service_rate.price
                )
            self.cost = self.service_rate.price

            user_obj = User.objects.get(username=self.user)
            user_obj.balance -= self.service_rate.price
            user_obj.save()

        elif self.status == 'not_active' and self.start_date:
            # Если в подписке пользователя выбирается статус `not_active`, то обнуляется дата для поля start_date и
            # expiration_date.
            self.start_date = None
            self.expiration_date = None
        elif self.status == 'not_active' and not self.start_date:
            self.status = 'process'

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

