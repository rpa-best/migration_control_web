from django.db import models
from v1_1.common_utils.file_paths import UploadPath
from v1_1.models.organization import Organization


class Worker(models.Model):
    GENDERS = (
        ('male', 'Мужчина'),
        ('female', 'Женщина'),
    )

    IDENTIFICATION_CARD = (
        ('passport', 'Паспорт'),
        ('residence_permit', 'Вид на жительство'),
        ('certificate_asylum', 'Свидетельство о предоставлении убежища')
    )

    STATUS = (
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
    position = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=50, choices=STATUS, default='accepted')
    phone = models.CharField(max_length=28, unique=True, blank=True, null=True,
                             default=None)
    registration_address = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True, null=True)
    avatar = models.ImageField(upload_to=UploadPath('image'), null=True)
    processing_personal_data = models.BooleanField(default=0)
    date_dismissal = models.DateField(blank=True, null=True)
    create_at = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False, null=True, blank=True)


class DocumentsWorker(models.Model):
    TYPES_DOCUMENTS = (
        ('passport', 'Паспорт'),
        ('migration_card', 'Миграционная карта'),
        ('registration', 'Регистрация'),
        ('patent', 'Патент'),
        ('paycheck', 'Чеки'),
        ('temporary_residence', 'Разрешение на временное проживание'),
        ('residence_permit', 'Вид на жительство'),
        ('certificate_asylum', 'Свидетельство о предоставлении временного убежища'),
        ('SNILS', 'СНИЛС'),
        ('INN', 'ИНН')
    )

    worker_id = models.ForeignKey(Worker, models.CASCADE)
    type_document = models.CharField(max_length=50, choices=TYPES_DOCUMENTS)
    series = models.CharField(max_length=30, null=True, blank=True)
    number = models.CharField(max_length=30, null=True, blank=True)
    date_issue = models.DateField(blank=True, null=True)
    issued_whom = models.CharField(max_length=150, null=True, blank=True)
    territory_action = models.CharField(max_length=150, blank=True, null=True)
    date_end = models.DateField(null=True, blank=True)
    archive = models.BooleanField(default=False, null=True, blank=True)


class FileDocuments(models.Model):
    document_id = models.ForeignKey(DocumentsWorker, on_delete=models.CASCADE)
    file_document = models.FileField(upload_to=UploadPath('documents'), null=True, blank=True)