import datetime
from django.db import models
from v1_1.common_utils.file_paths import UploadPath
from v1_1.models.organization import Organization
from v1_1.models.subscription import Subscription
from datetime import date, datetime, timedelta
from django.utils import timezone
from .user import HistoryPayment
from celery import shared_task
from django.db.models import Q


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
    date_employment = models.DateField(blank=True, null=True)
    position = models.CharField(max_length=255, blank=True)
    actual_work_address = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=50, choices=STATUS, default='vacancy')
    phone = models.CharField(max_length=28, unique=True, blank=True, null=True,
                             default=None)
    registration_address = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True, null=True)
    avatar = models.ImageField(upload_to=UploadPath('image'), null=True)
    processing_personal_data = models.BooleanField(default=0)
    date_dismissal = models.DateField(blank=True, null=True)
    create_at = models.DateTimeField(default=timezone.now)
    paid = models.BooleanField(default=False, null=True, blank=True)
    inn = models.CharField(max_length=30, null=True, blank=True)
    snils = models.CharField(max_length=30, null=True, blank=True)


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
        ('INN', 'ИНН'),
        ('VMI_policy', 'Добровольное медицинское страхование')
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

    def save(self, *args, **kwargs):
        """Переопределение метода save() для обновления данных в задаче, когда меняется значение поля date_end"""

        if self.type_document in ['passport', 'migration_card', 'registration', 'patent', 'paycheck',
                                  'temporary_residence', 'certificate_asylum']:
            pk = self.pk
            if Tasks.objects.filter(document_id=pk).exists():
                if self.archive:
                    Tasks.objects.get(document_id=pk).delete()
                    super(DocumentsWorker, self).save(*args, **kwargs)
                    return

                today = date.today()
                doc_task = Tasks.objects.get(document_id=pk)

                if self.date_end <= today:  # Документ просрочен?
                    doc_task.status = 'overdue'
                    days_until_expiration = 'Просрочено'
                elif self.date_end <= today + timedelta(days=30):
                    doc_task.status = 'open'
                    days_until_expiration = (self.date_end - today).days
                else:
                    # Удаление задачи, если документ актуален
                    doc_task.delete()
                    super(DocumentsWorker, self).save(*args, **kwargs)
                    return

                recommended_start_date = self.date_end - timedelta(days=7)

                # Есть ли изменения в дате документа?
                if str(doc_task.days_until_expiration) != str(days_until_expiration):
                    # Если дата окончания (date_end) документа изменилась, то в задаче поле `days_until_expiration` должно
                    # поменять значение
                    doc_task.days_until_expiration = days_until_expiration
                    doc_task.save()

                if doc_task.recommended_start_date != recommended_start_date:
                    # В таком же случае изменяется рекомендуемая дата
                    doc_task.recommended_start_date = recommended_start_date

                doc_task.save()
            else:
                today = date.today()

                if self.date_end <= today:  # Документ просрочен?
                    status = 'overdue'
                    days_until_expiration = 'Просрочено'
                    recommended_start_date = self.date_end - timedelta(days=7)
                    super(DocumentsWorker, self).save(*args, **kwargs)
                elif self.date_end <= today + timedelta(days=30):
                    status = 'open'
                    days_until_expiration = (self.date_end - today).days
                    recommended_start_date = self.date_end - timedelta(days=7)
                    super(DocumentsWorker, self).save(*args, **kwargs)
                else:
                    super(DocumentsWorker, self).save(*args, **kwargs)
                    return

                Tasks.objects.create(document_id=self, status=status, days_until_expiration=days_until_expiration,
                                     recommended_start_date=recommended_start_date)
        else:
            super(DocumentsWorker, self).save(*args, **kwargs)


class FileDocuments(models.Model):
    document_id = models.ForeignKey(DocumentsWorker, on_delete=models.CASCADE)
    file_document = models.FileField(upload_to=UploadPath('documents'), null=True, blank=True)


class Tasks(models.Model):
    STATUS = (
        ('done', 'Выполнено'),
        ('overdue', 'Просрочено'),
        ('open', 'Открыто'),
        ('shifted', 'Сдвинуто'),
        ('cancelled', 'Отменено')
    )

    document_id = models.OneToOneField(DocumentsWorker, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS)
    days_until_expiration = models.CharField(max_length=30)
    recommended_start_date = models.DateField()


@shared_task
def task_formation():
    """Celery функция для формирования задач, когда действия документа приближается к окончанию"""

    # Текущая дата
    today = datetime.now().date()

    # Необходимо, чтобы не возвращались документы у уволенных сотрудников
    filter_conditions = Q(date_end__lte=today) | Q(date_end__gte=today, date_end__lte=today + timedelta(days=30))

    # Необходимо, чтобы возвращались документы, которым остаётся 30 дней до окончания срока или которые уже
    # просрочены
    filter_conditions &= Q(date_end__lte=today) | Q(date_end__gte=today, date_end__lte=today + timedelta(days=30))

    filter_conditions &= Q(
        type_document__in=['passport', 'migration_card', 'registration', 'patent', 'paycheck', 'temporary_residence',
                           'certificate_asylum'])

    # Удаление из таблицы задач, у которых документ в архиве
    Tasks.objects.filter(document_id__archive=True).delete()

    expiring_documents = DocumentsWorker.objects.filter(filter_conditions, archive=False)

    for doc in expiring_documents:
        exists = Tasks.objects.filter(document_id=doc.pk).exists()

        today = date.today()

        if doc.date_end <= today:  # Документ просрочен?
            status = 'overdue'
            days_until_expiration = 'Просрочено'
        else:
            status = 'open'
            days_until_expiration = (doc.date_end - today).days

        recommended_start_date = doc.date_end - timedelta(days=7)

        if exists:  # Запись с таким вторичным ключом существует в задачах
            """В этом блоке обновление данных в задачах случае, когда дата окончания документа поменялась"""

            if doc.archive is True:
                Tasks.objects.get(document_id=doc.pk).delete()
            else:
                doc_task = Tasks.objects.get(document_id=doc.pk)
                if doc_task.status != 'shifted':
                    if str(doc_task.days_until_expiration) != str(days_until_expiration):   # Есть ли изменения в дате документа?
                        # Если дата окончания (date_end) документа изменилась, то в задаче поле `days_until_expiration` должно
                        # поменять значение
                        doc_task.days_until_expiration = days_until_expiration
                        doc_task.status = status
                        # Сохранение изменений
                        doc_task.save()

                    if doc_task.recommended_start_date != recommended_start_date:
                        # В таком же случае изменяется рекомендуемая дата
                        doc_task.recommended_start_date = recommended_start_date
                        doc_task.status = status
                        # Сохранение изменений
                        doc_task.save()
        else:   # Документ не содержится в задачах
            document = DocumentsWorker.objects.get(pk=doc.pk)
            Tasks.objects.create(   # Запись документа в задачах
                document_id=document,
                status=status,
                days_until_expiration=days_until_expiration,
                recommended_start_date=recommended_start_date
            )


@shared_task
def payment_for_worker():
    """Celery функция для учёта вычета из баланса за созданного работника, который просуществовал в базе хотя бы
    1 день"""

    current_datetime = timezone.now()
    twenty_four_hours_ago = current_datetime - timedelta(hours=24)

    # Фильтрация работников, которые созданы больше 1-го дня и не оплачены (paid=False)
    workers = Worker.objects.filter(
        create_at__lte=twenty_four_hours_ago,
        paid=False,
        status__in=['accepted', 'dismissed']
    )

    for worker in workers:
        owner = worker.organization.owner
        # Получение подписки владельца
        subscription = Subscription.objects.get(user=owner)
        # Цена за одного работника
        price = subscription.service_rate.cost_workers
        # Снятие денежных средств с баланса владельца подписки
        owner.balance -= price
        owner.save()

        # Работнику выставляется значение `Оплачен`, то есть с него больше уже не будет браться плата
        worker.paid = True
        worker.save()

        # Запись платежа за создание сотрудника в историю
        HistoryPayment.objects.create(
            user=owner,
            operation='Создание сотрудника',
            amount=price
        )