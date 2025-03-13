from django.contrib import admin
from v1_1.models import Country


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['title', ]
