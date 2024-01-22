from django.db import models
from v1_1.common_utils.file_paths import UploadPath
from v1_1.models.organization import Organization


class Worker(models.Model):
    GENDERS = (
        ('male', 'Male'),
        ('female', 'Female'),
    )

    IDENTIFICATION_CARD = (
        ('passport', 'Паспорт'),
        ('International_passport', 'Заграничный паспорт'),
        ('temporary_residence', 'Разрешение на временное проживание')
    )

    STATUS = (
        ('vacancy', 'Вакансия'),
        ('accepted', 'Принят'),
        ('dismissed', 'Уволен'),
    )

    name = models.CharField(max_length=150)
    surname = models.CharField(max_length=150)
    patronymic = models.CharField(max_length=150, blank=True, null=True)
    gender = models.CharField(max_length=50, choices=GENDERS)
    citizenship = models.CharField(max_length=255, blank=True)
    birthday = models.DateField(blank=True, null=True)
    place_birth = models.CharField(max_length=255, blank=True)
    identification_card = models.CharField(max_length=50, choices=IDENTIFICATION_CARD)
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS, default='vacancy')
    phone = models.CharField(max_length=28, unique=True, blank=True, null=True,
                             default=None)
    registration_address = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True, null=True)
    avatar = models.ImageField(upload_to=UploadPath('image'), null=True)
    processing_personal_data = models.BooleanField(default=0)
    date_dismissal = models.DateField(blank=True, null=True)


class DocumentsWorker(models.Model):
    TYPES_DOCUMENTS = (
        ('patent', 'Патент'),
        ('visa', 'Виза'),
        ('temporary_residence', 'Разрешение на временное проживание'),
        ('SNILS', 'СНИЛС'),
        ('INN', 'ИНН')
    )

    worker_id = models.ForeignKey(Worker, models.CASCADE)
    type_document = models.CharField(max_length=50, choices=TYPES_DOCUMENTS)
    file_document = models.ImageField(upload_to=UploadPath('image'), null=True)
    number = models.CharField(max_length=30)
    series = models.CharField(max_length=30)
    issued_whom = models.CharField(max_length=150)
    date_issue = models.DateField(blank=True, null=True)
    date_end = models.DateField(blank=True, null=True)


