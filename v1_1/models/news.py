from django.db import models
from v1_1.common_utils.file_paths import UploadPath
from v1_1.models.organization import Organization
from v1_1.models.user import User
from django.utils import timezone


class Tags(models.Model):
    name = models.CharField(max_length=100, blank=True)


class News(models.Model):
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField()
    date_publication = models.DateTimeField(default=timezone.now, null=True)
    author = models.ForeignKey(User, models.CASCADE, blank=True, null=True)


class TagsNew(models.Model):
    new = models.ForeignKey(News, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tags, on_delete=models.CASCADE)
