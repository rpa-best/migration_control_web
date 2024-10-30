from django.contrib import admin
from ..models.subscription import Subscription, ServiceRate, Benefits, BenefitsServiceRate


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_service_rate_type', 'number_organizations', 'number_workers', 'cost', 'status',
                    'start_date', 'expiration_date']
    inlines = []

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
    list_display = ['type_tariff', 'name', 'cost_organizations', 'cost_workers', 'price']

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





