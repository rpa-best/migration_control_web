from django.db import models
from v1_1.common_utils.file_paths import UploadPath
from v1_1.models.organization import Organization
from v1_1.models.user import User
from django.utils import timezone


class Tags(models.Model):
    name = models.CharField('Тег', max_length=100, blank=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class News(models.Model):
    title = models.CharField('Заголовок', max_length=255, blank=True)
    content = models.TextField('Контент',)
    date_publication = models.DateTimeField('Дата публикации', default=timezone.now, null=True)
    author = models.ForeignKey(User, models.CASCADE, verbose_name='Автор', blank=True, null=True)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'


class TagsNew(models.Model):
    new = models.ForeignKey(News, on_delete=models.CASCADE, verbose_name='Новость')
    tag = models.ForeignKey(Tags, on_delete=models.CASCADE, verbose_name='Тег')

    class Meta:
        verbose_name = 'Тег новости'
        verbose_name_plural = 'Теги новости'
