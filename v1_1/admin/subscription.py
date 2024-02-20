from django.contrib import admin
from ..models.subscription import Subscription, ServiceRate


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_service_rate_type', 'number_organizations', 'number_workers', 'default_cost', 'status',
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