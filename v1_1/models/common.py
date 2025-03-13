from django.db import models


class Country(models.Model):
    title = models.CharField(max_length=250)

    class Meta:
        verbose_name = 'Страну'
        verbose_name_plural = 'Страны'