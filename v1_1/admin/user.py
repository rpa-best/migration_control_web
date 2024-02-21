from django.contrib import admin
from ..models.user import BalanceTransfer


@admin.register(BalanceTransfer)
class BalanceTransferAdmin(admin.ModelAdmin):
    list_display = ['user', 'cost', 'date', 'type']

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == 'type':
            kwargs['choices'] = [('', 'Выберите операцию')] + list(BalanceTransfer.TYPE)
            kwargs['empty_label'] = 'Выберите операцию'
        return super().formfield_for_choice_field(db_field, request, **kwargs)
