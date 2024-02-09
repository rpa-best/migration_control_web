import string
import random
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from v1_1.common_utils.file_paths import UploadPath
from v1_1.common_utils.pvc import get_random_integer, send_email, send_sms


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(blank=True, null=True)
    username = models.EmailField(max_length=150, unique=True)
    password = models.CharField(max_length=150)
    phone = models.CharField(max_length=28, unique=True, blank=True, null=True, default=None)
    name = models.CharField(max_length=150, blank=True, null=True)
    surname = models.CharField(max_length=150, blank=True, null=True)
    patronymic = models.CharField(max_length=150, blank=True, null=True)
    avatar = models.ImageField(upload_to=UploadPath('image'), null=True)
    birthday = models.DateField(blank=True, null=True)
    is_staff = models.BooleanField(default=False, null=True)
    date_joined = models.DateTimeField(default=timezone.now, null=True)
    is_superuser = models.BooleanField(default=0, null=True)
    is_active = models.BooleanField(default=1, null=True)
    is_official = models.BooleanField(default=False, null=True)
    pvc = models.CharField(max_length=150, null=True, blank=True)

    USERNAME_FIELD = 'username'

    def regenerate_pvc(self, is_send=True):
        new_pvc = get_random_integer(6)
        self.save_pvc(new_pvc)
        if is_send:
            send_sms(
                self.phone,
                f"{new_pvc}"
            )

    def save_pvc(self, pvc):
        self.pvc = make_password(pvc)
        self.save()
        self.set_password()

    def regenerate_and_send_password(self):
        # Генерирация пароля из допустимых символов
        password = ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(12))
        self.set_password(password)

        send_email(self.username, 'Код подтверждения для Миграскопа', f'Вас зарегистрировали в Миграскопе. '
                                                                      f'Ваш пароль для входа: {password}')
        self.save()


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
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, to_field='username')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'token_blacklist_outstandingtoken'


def generate_pvc():
    return get_random_integer(6)


class UserPvc(models.Model):
    email = models.CharField(unique=True, max_length=255)
    pvc = models.CharField(max_length=10, default=generate_pvc)

    def send_pvc(self):
        self.pvc = generate_pvc()
        send_email(self.email, 'Код подтверждения для Миграскопа', self.pvc)
        self.save()


class RegistrationLog(models.Model):
    ip = models.CharField(max_length=255)
    user_agent = models.TextField()
    registration_time = models.DateTimeField(auto_now_add=True)