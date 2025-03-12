from django.contrib import admin

from . import User
from ..models import HistoryPayment
from ..models.subscription import Subscription, ServiceRate, Benefits, BenefitsServiceRate
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models import Model


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_service_rate_type', 'status',
                    'start_date', 'expiration_date']
    inlines = []

    def save_model(self, request, obj: Model, form, change):
        try:
            if obj.status == 'active':
                user_obj = User.objects.get(username=obj.user)

                # Проверка на достаточность средств
                if user_obj.balance < obj.service_rate.price:
                    raise ValidationError(
                        _('У пользователя недостаточно денежных средств на балансе для одобрения подписки'))

                if obj.service_rate.type_tariff == 'standard':
                    HistoryPayment.objects.create(
                        user=obj.user,
                        operation='Покупка стандартной подписки',
                        amount=obj.service_rate.price
                    )
                elif obj.service_rate.type_tariff == 'pro':
                    HistoryPayment.objects.create(
                        user=obj.user,
                        operation='Покупка про подписки',
                        amount=obj.service_rate.price
                    )
                user_obj.balance -= obj.service_rate.price
                user_obj.save()

            elif obj.status == 'not_active' and obj.start_date:
                obj.start_date = None
                obj.expiration_date = None
            elif obj.status == 'not_active' and not obj.start_date:
                obj.status = 'process'

            super().save_model(request, obj, form, change)

        except ValidationError as e:
            # Сообщение об ошибке
            self.message_user(request, str(e), level=messages.ERROR)

    def get_service_rate_type(self, obj):
        return obj.service_rate.get_type_tariff_display()

    get_service_rate_type.short_description = 'Тариф'

    def get_status_display(self, obj):
        return dict(Subscription.STATUS)[obj.status]

    get_status_display.short_description = 'Статус'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'service_rate':
            kwargs['queryset'] = ServiceRate.objects.all()
            kwargs['empty_label'] = 'Выберите тариф'
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class BenefitsServiceRate(admin.TabularInline):
    model = BenefitsServiceRate
    extra = 1


@admin.register(Benefits)
class BenefitsAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(ServiceRate)
class ServiceRateAdmin(admin.ModelAdmin):
    list_display = ['type_tariff', 'name', 'description', 'number_organizations', 'number_workers',
                    'cost_organizations', 'cost_workers', 'price']

    # inlines = []

    inlines = [BenefitsServiceRate]

    # def get_benefit(self, obj):
    #     return obj.benefits.name
    #
    # get_benefit.short_description = 'Выгода'
    #
    # def get_status_display(self, obj):
    #     return dict(Subscription.STATUS)[obj.status]
    #
    # get_status_display.short_description = 'Статус'
    #
    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == 'benefit':
    #         kwargs['queryset'] = Benefits.objects.all()
    #         kwargs['empty_label'] = 'Выберите выгоду'
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)





