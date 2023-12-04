from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from v1_1.common_utils.file_paths import UploadPath


class User(AbstractUser):
    email = models.EmailField(_("email address"), unique=True, error_messages={
        "unique": _("A user with that email already exists."),
    })
    username = models.EmailField(max_length=150, unique=True)
    password = models.CharField(max_length=20)
    phone = models.CharField(max_length=28, unique=True, blank=True, null=True,
                             default=None)
    name = models.CharField(max_length=150, blank=True, null=True)
    surname = models.CharField(max_length=150, blank=True, null=True)
    lastname = models.CharField(max_length=150, blank=True, null=True)
    avatar = models.ImageField(upload_to=UploadPath('image'))
    is_owner = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    is_superuser = models.BooleanField(default=0)
    is_active = models.BooleanField(default=1)
    is_official = models.BooleanField(default=False)
