import re
from datetime import timedelta
from django.utils.datetime_safe import date
from rest_framework import serializers
from v1_1.apies.DaData import AddressSearch
from v1_1.common_utils.custom_handler import CustomValidationError
from v1_1.models import Country
from v1_1.models.organization import OrganizationUser
from v1_1.models.subscription import Subscription
from v1_1.models.worker import Worker, DocumentsWorker, FileDocuments
import copy


class CreateWorkerSerializer(serializers.ModelSerializer):
    patronymic = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)
    email = serializers.CharField(required=False)

    class Meta:
        model = Worker
        fields = (
            'id',
            'name',
            'surname',
            'patronymic',
            'gender',
            'citizenship',
            'birthday',
            'place_birth',
            'identification_card',
            'organization',
            'date_employment',
            'position',
            'actual_work_address',
            'status',
            'phone',
            'registration_address',
            'email',
            'avatar',
            'processing_personal_data',
            'date_dismissal',
            'inn',
            'snils'
        )

    def validate_organization(self, value):
        user = self.context['request'].user.username
        # Можно указать только ту организацию, в которой работает пользователь.
        if not OrganizationUser.objects.filter(organization=value, user_id=user).exists():
            raise CustomValidationError({'organization': 'Вы не являетесь сотрудником этой организации'})

        return value

    @staticmethod
    def validate_email(value):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise CustomValidationError({'email': 'Введён некорректный формат почты'})

        return value

    def validate(self, data):
        if 'phone' in data:
            if Worker.objects.filter(organization=data['organization'].id, phone=data['phone']).exists():
                raise CustomValidationError({'phone': 'Номер телефона занят другим сотрудником'})

        return data

    def create(self, validated_data):
        # Получение владельца организации
        organization_owner = OrganizationUser.objects.filter(organization=validated_data['organization'].id, role='owner').first()
        # Проверка на наличие активной подписки у владельца организации
        subscription = Subscription.objects.filter(user=organization_owner.user, status='active').first()
        if not subscription:
            raise CustomValidationError({'error': "У владельца нет активной подписки."})

        # Получение максимального количества работников, которых можно создать
        max_employees = subscription.service_rate.number_workers

        # Получение списка работников, созданных пользователем
        count_worker = Worker.objects.filter(organization__owner=organization_owner.user).count()

        # Проверка на превышение лимита по количеству создаваемых работников
        if count_worker >= max_employees:
            if organization_owner.user.balance >= subscription.service_rate.cost_workers:
                instance: Worker = super().create(validated_data)
                instance.save()
                return instance
            else:
                raise CustomValidationError({'error': 'Вы достигли максимального лимита на создание сотрудников.'})

        validated_data['paid'] = True

        instance: Worker = super().create(validated_data)
        instance.save()
        return instance


class WorkerSerializer(serializers.ModelSerializer):
    patronymic = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    registration_address = serializers.CharField(required=False)
    identification_card = serializers.ChoiceField(choices=Worker.IDENTIFICATION_CARD)
    position = serializers.CharField(required=False)
    actual_work_address = serializers.CharField(required=False)
    status = serializers.CharField(required=False)
    avatar = serializers.ImageField(required=False)
    date_dismissal = serializers.DateField(required=False)
    inn = serializers.CharField(required=False)
    snils = serializers.CharField(required=False)

    class Meta:
        model = Worker
        fields = (
            'id',
            'name',
            'surname',
            'patronymic',
            'gender',
            'citizenship',
            'birthday',
            'place_birth',
            'identification_card',
            'organization',
            'date_employment',
            'position',
            'actual_work_address',
            'status',
            'phone',
            'registration_address',
            'email',
            'avatar',
            'processing_personal_data',
            'date_dismissal',
            'inn',
            'snils'
        )

    def validate_organization(self, value):
        user = self.context['request'].user.username
        # Можно указать только ту организацию, в которой работает пользователь.
        if not OrganizationUser.objects.filter(organization=value, user_id=user).exists():
            raise CustomValidationError({'organization': 'Вы не являетесь сотрудником этой организации'})

        return value

    @staticmethod
    def validate_email(value):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise CustomValidationError({'email': 'Введён некорректный формат почты'})

        return value

    def validate_registration_address(self, value):
        if AddressSearch(value) is not None:
            return AddressSearch(value)
        return value


class DocumentsWorkerSerializer(serializers.ModelSerializer):
    # Параметр для определения обязательных полей для каждого типа документа
    REQUIRED_FIELDS = {
        'passport': ['number', 'issued_whom', 'date_issue', 'date_end'],
        'migration_card': ['series', 'number', 'date_issue', 'date_end'],
        'registration': ['date_issue', 'date_end'],
        'patent': ['date_issue', 'date_end'],
        'paycheck': ['date_end'],
        'temporary_residence': ['series', 'number', 'issued_whom', 'date_issue', 'date_end'],
        'residence_permit': ['series', 'number', 'issued_whom', 'date_issue'],
        'certificate_asylum': ['series', 'number', 'issued_whom', 'date_issue', 'date_end'],
        'SNILS': ['number'],
        'INN': ['number'],
        'vmi_policy': ['series', 'number', 'issued_whom', 'date_issue', 'date_end']
    }

    type_document = serializers.ChoiceField(choices=DocumentsWorker.TYPES_DOCUMENTS, required=False)
    file_documents = serializers.ListField(child=serializers.FileField(required=False), write_only=True, required=False)
    archive = serializers.BooleanField(required=False)
    status = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = DocumentsWorker
        fields = (
            'id',
            'file_documents',
            'type_document',
            'series',
            'number',
            'date_issue',
            'issued_whom',
            'territory_action',
            'date_end',
            'archive',
            'status'
        )
        read_only_fields = ('id', 'worker_id', 'status')

    def get_status(self, obj):
        if obj.type_document in ['passport', 'migration_card', 'registration', 'patent', 'paycheck',
                                  'temporary_residence', 'certificate_asylum', 'vmi_policy']:
            today = date.today()

            if obj.date_end is None:
                return 'not overdue'
            if obj.date_end < today:  # Документ просрочен?
                return 'overdue'
            elif obj.date_end <= today + timedelta(days=30):
                return 'close to overdue'
            else:
                return 'not overdue'
        else:
            return 'not overdue'

    def validate(self, data):
        if not Worker.objects.filter(pk=self.context['request'].parser_context['kwargs'].get('worker_id')).exists():
            raise CustomValidationError({'worker_id':  'Сотрудник не найден'})

        if 'archive' not in data:
            data['archive'] = False

        max_file_size = 3 * 1024 * 1024  # 3 MB
        for f in data.get('file_documents') or []:
            if f and hasattr(f, 'size') and f.size > max_file_size:
                raise CustomValidationError({'file_documents': f'Файл {f.name} превышает допустимый размер 3 МБ'})

        worker_id = self.context['request'].parser_context['kwargs'].get('worker_id')
        type_document = data.get('type_document')
        archive = data.get('archive')

        doc_task = self.context['request'].parser_context['kwargs'].get('doc_task_id')
        if not doc_task:
            if self.instance:  # Если это редактирование записи
                # Проверка, существуют ли другие активные документы у сотрудника с такими же параметрами, за исключением
                # текущего документа self.instance.id
                existing_documents = DocumentsWorker.objects.filter(worker_id=worker_id, type_document=type_document,
                                                                    archive=False).exclude(id=self.instance.id)
                if not archive and existing_documents.exists():
                    raise CustomValidationError({'error': 'У сотрудника уже есть такой активный документ. '
                                                          'Для добавления текущего документа необходимо один '
                                                          'из документов пометить в архив'})

                if archive:
                    if existing_documents.exists():
                        raise CustomValidationError({'error': 'У сотрудника уже есть такой активный документ. '
                                                              'Для добавления текущего документа необходимо один '
                                                              'из документов пометить в архив'})
            else:  # Создание новой записи
                existing_documents = DocumentsWorker.objects.filter(worker_id=worker_id, type_document=type_document,
                                                                    archive=False)
                if not archive and existing_documents.exists():
                    raise CustomValidationError({'error': 'У сотрудника уже есть такой активный документ. '
                                                          'Для добавления текущего документа необходимо один '
                                                          'из документов пометить в архив'})

        return data

    def create(self, validated_data):
        type_document = validated_data['type_document']

        if type_document == '' or type_document is None:
            raise CustomValidationError({'type_document': 'Выберите тип документа'})

        # Проверка, что все обязательные поля для выбранного типа документа заполнены
        for field in self.REQUIRED_FIELDS[type_document]:
            if field not in validated_data:
                raise CustomValidationError({field: 'Это поле обязательно для заполнения'})

        # Получение id работника из url пути
        validated_data['worker_id'] = Worker.objects.filter(pk=self.context['request'].parser_context['kwargs'].
                                                            get('worker_id')).first()

        # Удаление ключа `file_documents` из словаря, поскольку он не содержится в модели `DocumentsWorker`,
        # но есть в модели `FileDocuments`
        # Создание записей для модели MigrationAddress
        file_documents = validated_data.pop('file_documents') if 'file_documents' in validated_data else []

        instance: DocumentsWorker = super(DocumentsWorkerSerializer, self).create(validated_data)
        instance.save()

        # Добавление файлов документов
        for file_document in file_documents:
            FileDocuments.objects.create(document_id=instance, file_document=file_document)

        response_data = {
            'id': instance.id,
            'type_document': instance.type_document,
            'series': instance.series,
            'number': instance.number,
            'date_issue': instance.date_issue,
            'issued_whom': instance.issued_whom,
            'territory_action': instance.territory_action,
            'date_end': instance.date_end,
            'archive': instance.archive
        }

        return response_data

    def update(self, instance, validated_data):
        file_documents = validated_data.pop('file_documents') if 'file_documents' in validated_data else []

        instance = super(DocumentsWorkerSerializer, self).update(instance, validated_data)
        instance.save()

        for file_document in file_documents:
            FileDocuments.objects.create(document_id=instance, file_document=file_document)

        return instance


class FileDocumentsSerializer(serializers.ModelSerializer):
    file_document = serializers.FileField(required=True)

    MAX_FILE_SIZE = 3 * 1024 * 1024  # 3 MB

    class Meta:
        model = FileDocuments
        fields = '__all__'
        read_only_fields = ('document_id',)

    def validate(self, data):
        document_id = self.context['request'].parser_context['kwargs'].get('document_id')
        # Проверка на существование документа работника.
        if not DocumentsWorker.objects.filter(pk=document_id).exists():
            raise CustomValidationError({'document_id': 'Документ не найден'})

        # Проверка на количество загруженных файлов для документа
        if FileDocuments.objects.filter(document_id=document_id).count() >= 20:
            raise CustomValidationError({'file_document': 'Превышено максимальное количество файлов для документа'})

        # Проверка на размер файла
        file_document = data.get('file_document')
        if file_document and file_document.size > self.MAX_FILE_SIZE:
            raise CustomValidationError({'file_document': 'Размер файла не должен превышать 3 МБ'})

        return data

    def create(self, validated_data):
        document_id = self.context['request'].parser_context['kwargs'].get('document_id')
        document_worker = DocumentsWorker.objects.get(pk=document_id)

        file = FileDocuments.objects.create(document_id=document_worker, file_document=validated_data['file_document'])

        response_date = {
            'document_id': file.id,
            'file_document': self.context['request'].build_absolute_uri(file.file_document.url)
        }

        return response_date


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'