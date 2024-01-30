import re
from rest_framework import serializers
from v1_1.common_utils.custom_handler import CustomValidationError
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

    class Meta:
        model = Worker
        fields = '__all__'


class DocumentsWorkerSerializer(serializers.ModelSerializer):
    type_document = serializers.ChoiceField(choices=DocumentsWorker.TYPES_DOCUMENTS)
    file_document = serializers.FileField(required=False)

    class Meta:
        model = DocumentsWorker
        fields = (
            'file_document',
            'type_document',
            'series',
            'number',
            'date_issue',
            'issued_whom',
            'territory_action',
            'date_end',
            'archive'
        )
        read_only_fields = ('worker_id',)

    def validate(self, data):
        if not Worker.objects.filter(pk=self.context['request'].parser_context['kwargs'].get('worker_id')).exists():
            raise CustomValidationError({'worker_id':  'Сотрудник не найден'})
        return data

    def create(self, validated_data):
        validated_data['worker_id'] = Worker.objects.filter(pk=self.context['request'].parser_context['kwargs'].get('worker_id')).first()
        # независимое копирование словаря
        file_document_data = copy.deepcopy(validated_data)
        # Удаление ключа `file_documents` из словаря, поскольку он не содержится в модели `DocumentsWorker`,
        # но есть в модели `FileDocuments`
        validated_data.pop('file_document', None)

        instance: DocumentsWorker = super(DocumentsWorkerSerializer, self).create(validated_data)
        instance.save()

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

        if file_document_data:
            file_document = FileDocuments.objects.create(document_id=instance, file_document=file_document_data['file_document'])
            response_data.update({
                'file_document_id': file_document.id,
                'file_document': self.context['request'].build_absolute_uri(file_document.file_document.url)
            })

        return response_data
