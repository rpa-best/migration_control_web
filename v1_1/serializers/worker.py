import re
from rest_framework import serializers
from v1_1.apies.DaData import AddressSearch
from v1_1.common_utils.custom_handler import CustomValidationError
from v1_1.models.organization import OrganizationUser
from v1_1.models.subscription import Subscription
from v1_1.models.worker import Worker, DocumentsWorker, FileDocuments
import copy


class CreateWorkerSerializer(serializers.ModelSerializer):
    patronymic = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    identification_card = serializers.CharField(source='get_identification_card_display')

    class Meta:
        model = Worker
        fields = (
            'avatar',
            'organization',
            'name',
            'surname',
            'patronymic',
            'citizenship',
            'identification_card',
            'phone',
            'email'
        )

    def validate_organization(self, value):
        user = self.context['request'].user.username
        # Можно указать только ту организацию, в которой работает пользователь.
        if not OrganizationUser.objects.filter(organization=value, user_id=user).exists():
            raise CustomValidationError({'organization': 'Вы не являетесь сотрудником этой организации'})

        return value

    @staticmethod
    def validate_phone(value):
        phone_pattern = re.compile(r'^\+?1?\d{9,15}$')
        if not phone_pattern.match(value):
            raise CustomValidationError({'phone': 'Введён некорректный номер телефона'})

        return value

    @staticmethod
    def validate_email(value):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise CustomValidationError({'email': 'Введён некорректный формат почты'})

        return value

    def validate(self, data):
        if Worker.objects.filter(organization=data['organization'].id, phone=data['phone']).exists():
            raise CustomValidationError({'phone': 'Номер телефона занят другим работником'})

        # Получение владельца организации
        organization_owner = OrganizationUser.objects.filter(organization=data['organization'].id, role='owner').first()
        # Проверка на наличие активной подписки у владельца организации
        subscription = Subscription.objects.filter(user=organization_owner.user, status='active').first()
        if not subscription:
            raise CustomValidationError({'error': "У владельца нет активной подписки."})

        # Получение максимального количества работников, которых можно создать
        max_employees = subscription.service_rate.number_employees
        #
        # # Получение списка ИНН работников, созданных пользователем
        # user_employees = Worker.objects.filter(organization__owner=organization_owner.user).values_list('inn',
        #                                                                                                 flat=True)
        # # Подсчет количества уникальных ИНН работников
        # unique_employees = len(set(user_employees))

        # Получение списка работников, созданных пользователем
        user_employees = Worker.objects.filter(organization__owner=organization_owner.user).count()

        unique_employees = user_employees

        # Проверка на превышение лимита по количеству создаваемых работников
        if unique_employees >= max_employees:
            raise CustomValidationError({'error': 'Вы достигли максимального лимита на создание сотрудников.'})

        return data


class WorkerSerializer(serializers.ModelSerializer):
    registration_address = serializers.CharField()
    identification_card = serializers.CharField(source='get_identification_card_display')

    class Meta:
        model = Worker
        fields = '__all__'

    def validate_registration_address(self, value):
        if AddressSearch(value) is not None:
            return AddressSearch(value)
        return value


class DocumentsWorkerSerializer(serializers.ModelSerializer):
    # Параметр для определения обязательных полей для каждого типа документа
    REQUIRED_FIELDS = {
        'passport': ['series', 'number', 'issued_whom', 'date_issue', 'date_end'],
        'migration_card': ['number', 'date_issue', 'date_end'],
        'registration': ['date_issue', 'date_end'],
        'patent': ['date_issue', 'date_end'],
        'paycheck': ['date_end'],
        'temporary_residence': ['series', 'number', 'issued_whom', 'date_issue', 'date_end'],
        'residence_permit': ['series', 'number', 'issued_whom', 'date_issue', 'date_end'],
        'certificate_asylum': ['series', 'number', 'issued_whom', 'date_issue', 'date_end'],
        'SNILS': ['number'],
        'INN': ['number']
    }

    type_document = serializers.ChoiceField(choices=DocumentsWorker.TYPES_DOCUMENTS)
    file_documents = serializers.ListField(child=serializers.FileField(required=False), write_only=True, required=False)
    archive = serializers.BooleanField(required=False)

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
            'archive'
        )
        read_only_fields = ('id', 'worker_id',)

    def validate(self, data):
        if not Worker.objects.filter(pk=self.context['request'].parser_context['kwargs'].get('worker_id')).exists():
            raise CustomValidationError({'worker_id':  'Сотрудник не найден'})

        if 'archive' not in data:
            data['archive'] = False

        if 'type_document' in data:
            worker_id = self.context['request'].parser_context['kwargs'].get('worker_id')

            if DocumentsWorker.objects.filter(type_document=data['type_document'], worker_id=worker_id).exists():
                if data['archive'] is False:
                    try:
                        if (DocumentsWorker.objects.get(type_document=data['type_document'], worker_id=worker_id,
                                                        archive=False).archive
                                is False):

                            raise CustomValidationError({'error':  'У сотрудника уже есть такой активный документ. '
                                                                   'Для добавления текущего документа необходимо один '
                                                                   'из документов пометить в архив'})
                    except Exception:
                        raise CustomValidationError({'error': 'У сотрудника уже есть такой активный документ. '
                                                              'Для добавления текущего документа необходимо один '
                                                              'из документов пометить в архив'})

        return data

    def create(self, validated_data):
        type_document = validated_data['type_document']

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


class FileDocumentsSerializer(serializers.ModelSerializer):
    file_document = serializers.FileField(required=True)

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
