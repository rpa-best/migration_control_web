from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

from v1_1.common_utils.file_paths import UploadPath


class User(AbstractBaseUser, PermissionsMixin):
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
    avatar = models.ImageField(upload_to=UploadPath('image'), null=True)
    is_owner = models.BooleanField(default=False, null=True)
    is_staff = models.BooleanField(default=False, null=True)
    date_joined = models.DateTimeField(default=timezone.now, null=True)
    is_superuser = models.BooleanField(default=0, null=True)
    is_active = models.BooleanField(default=1, null=True)
    is_official = models.BooleanField(default=False, null=True)

    USERNAME_FIELD = "username"


class UserOutstandingToken(OutstandingToken):
    DEVICES_IDS = [
        [0, "Desktop"],
        [1, "Android"],
        [2, "iOS"],
        [3, "Mobile WEB"],
        [4, "DWED infomat"],
        [5, "TMED"],
    ]

    device_id = models.IntegerField(choices=DEVICES_IDS, default=0)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    mac_address = models.CharField(max_length=128, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, to_field='username')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'token_blacklist_outstandingtoken'

