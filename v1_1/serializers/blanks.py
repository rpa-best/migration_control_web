from rest_framework import serializers
from v1_1.common_utils.custom_handler import CustomValidationError
from v1_1.models.organization import OrganizationUser, Organization, ResponsiblePersons
from v1_1.models.worker import Worker


class SearchWorkerSerializer(serializers.ModelSerializer):
    inn = serializers.SerializerMethodField()
    organization = serializers.SerializerMethodField()

    def get_inn(self, obj):
        try:
            worker_documents = DocumentsWorker.objects.filter(worker_id=obj.id, type_document='INN').first()
            if worker_documents:
                return worker_documents.number
        except Exception:
            return ""

    def get_organization(self, obj):
        return obj.organization.name

    class Meta:
        model = Worker
        fields = ['id', 'surname', 'name', 'patronymic', 'inn', 'organization']


# Трудовой договор
class EmploymentContractSerializer(serializers.Serializer):
    CONTRACT_TYPE = (
        ('perpetual', 'Бессрочный договор'),
        ('urgent', 'Срочный договор')
    )

    worker_id = serializers.IntegerField()
    number = serializers.CharField(write_only=True, max_length=10)
    position = serializers.CharField(write_only=True, max_length=30)
    salary = serializers.IntegerField(write_only=True)
    contract_type = serializers.ChoiceField(choices=CONTRACT_TYPE)
    start_date = serializers.DateField(write_only=True)
    end_date_urgent = serializers.DateField(required=False)
    cause = serializers.CharField(required=False)
    start_time = serializers.TimeField(write_only=True)
    end_time = serializers.TimeField(write_only=True)

    def validate_worker_id(self, value):
        if not Worker.objects.filter(pk=value).exists():
            raise CustomValidationError({'worker_id': 'Сотрудника не существует'})

        user = self.context['request'].user.username
        list_organizations = []
        for organization in OrganizationUser.objects.filter(user_id=user):
            list_organizations.append(organization.organization_id)

        #Можно формировать бланки только для своих работников
        if Worker.objects.get(pk=value).organization_id not in list_organizations:
            raise CustomValidationError({'worker_id': 'Сотрудник не из вашей компании'})

    def create(self, validated_data):
        return validated_data


class SuspensionOrderSerializer(serializers.Serializer):
    REASON_SUSPENSION = (
        ('valid_residence_permit', 'действующего Вида на жительство'),
        ('valid_patent', 'действующего патента'),
        ('valid_temporary_residence_permit', 'действующего разрешения на временное проживание'),
        ('getting_vaccinated', 'справки о прохождении вакцинации от кори или отказа от вакцинации, заверенного врачом'),
        ('passing_medical_examination', 'справки о прохождении медосмотра'),
        ('passing_analysis', 'справки о сдаче анализа крови на антитела'),
        ('checks', 'чеков, подтверждающих авансовую оплату за патент'),
    )

    worker_id = serializers.IntegerField(required=True)
    number = serializers.CharField(write_only=True, max_length=10, required=True)
    start_date = serializers.DateField(write_only=True, required=True)
    reason_suspension = serializers.ChoiceField(choices=REASON_SUSPENSION, required=True)
    first_manager_id = serializers.IntegerField(required=True)
    second_manager_id = serializers.IntegerField(required=True)

    def validate_worker_id(self, value):
        if not Worker.objects.filter(pk=value).exists():
            raise CustomValidationError({'worker_id': 'Сотрудник не существует'})

        user = self.context['request'].user.username
        list_organizations = []
        for organization in OrganizationUser.objects.filter(user_id=user):
            list_organizations.append(organization.organization_id)

        #Можно формировать бланки только для своих работников
        if Worker.objects.get(pk=value).organization_id not in list_organizations:
            raise CustomValidationError({'worker_id': 'Сотрудник не из вашей компании'})

    def validate_first_manager_id(self, value):
        if not ResponsiblePersons.objects.filter(pk=value).exists():
            raise CustomValidationError({'first_manager_id': 'Менеджера не существует'})

        user = self.context['request'].user.username
        list_organizations = []
        for organization in OrganizationUser.objects.filter(user_id=user):
            list_organizations.append(organization.organization_id)

        if ResponsiblePersons.objects.get(pk=value).organization not in list_organizations:
            raise CustomValidationError({'first_manager_id': 'Менеджер не из вашей компании'})

        return value

    def validate_second_manager_id(self, value):
        if not ResponsiblePersons.objects.filter(pk=value).exists():
            raise CustomValidationError({'second_manager_id': 'Менеджера не существует'})

        user = self.context['request'].user.username
        list_organizations = []
        for organization in OrganizationUser.objects.filter(user_id=user):
            list_organizations.append(organization.organization_id)

        if ResponsiblePersons.objects.get(pk=value).organization not in list_organizations:
            raise CustomValidationError({'second_manager_id': 'Менеджер не из вашей компании'})

        return value

    def create(self, validated_data):
        return validated_data


# Платёжное поручение
class GenerationPaymentOrderSerializer(serializers.Serializer):
    worker_id = serializers.IntegerField(required=True)
    number_months = serializers.IntegerField(write_only=True, required=True)

    def validate_worker_id(self, value):
        if not Worker.objects.filter(pk=value).exists():
            raise CustomValidationError({'worker_id': 'Сотрудника не существует'})

        user = self.context['request'].user.username
        list_organizations = []
        for organization in OrganizationUser.objects.filter(user_id=user):
            list_organizations.append(organization.organization_id)

        #Можно формировать бланки только для своих работников
        if Worker.objects.get(pk=value).organization_id not in list_organizations:
            raise CustomValidationError({'worker_id': 'Сотрудник не из вашей компании'})

    def create(self, validated_data):
        return validated_data


class ServiceSerializer(serializers.Serializer):
    name = serializers.CharField()
    price = serializers.IntegerField()


class ContractProvisionPaidServicesSerializer(serializers.Serializer):
    worker_id = serializers.IntegerField(required=True)
    number = serializers.CharField(write_only=True, max_length=10, required=True)
    start_date = serializers.DateField(write_only=True, required=True)
    end_date = serializers.DateField(write_only=True, required=True)
    address = serializers.CharField(write_only=True, max_length=250, required=True)
    services = ServiceSerializer(many=True)

    def validate_worker_id(self, value):
        if not Worker.objects.filter(pk=value).exists():
            raise CustomValidationError({'worker_id': 'Сотрудника не существует'})

        user = self.context['request'].user.username
        list_organizations = []
        for organization in OrganizationUser.objects.filter(user_id=user):
            list_organizations.append(organization.organization_id)

        #Можно формировать бланки только для своих работников
        if Worker.objects.get(pk=value).organization_id not in list_organizations:
            raise CustomValidationError({'worker_id': 'Сотрудник не из вашей компании'})

    def create(self, validated_data):
        return validated_data


# Уведомление о заключении
class NoticeConclusionSerializer(serializers.Serializer):
    BASES = (
        ('employment_contract', 'Трудовой договор'),
        ('civil_contract', 'Гражданско-правовой договор на выполнение работ (оказание услуг)')
    )
    TYPE_PERSON = (
        ('person_proxy', 'Человек, который подаёт документы по доверенности'),
        ('director', 'Директор')
    )

    worker_id = serializers.IntegerField(required=True)
    name_territorial_body = serializers.CharField(max_length=100)
    position = serializers.CharField(max_length=100)
    base = serializers.ChoiceField(choices=BASES)
    start_date = serializers.DateField(write_only=True)
    address = serializers.CharField(max_length=100)
    person = serializers.ChoiceField(choices=TYPE_PERSON)
    full_name = serializers.CharField(max_length=55, required=False)
    series = serializers.CharField(required=False)
    number = serializers.CharField(required=False)
    date_issue = serializers.DateField(required=False)
    issued_by = serializers.CharField(max_length=100, required=False)

    def validate_worker_id(self, value):
        if not Worker.objects.filter(pk=value).exists():
            raise CustomValidationError({'worker_id': 'Работника не существует'})

        user = self.context['request'].user.username
        list_organizations = []
        for organization in OrganizationUser.objects.filter(user_id=user):
            list_organizations.append(organization.organization_id)

        #Можно формировать бланки только для своих работников
        if Worker.objects.get(pk=value).organization_id not in list_organizations:
            raise CustomValidationError({'worker_id': 'Работника не из вашей организации'})

    def create(self, validated_data):
        return validated_data


class NoticeTerminationSerializer(serializers.Serializer):
    BASES = (
        ('employment_contract', 'Трудовой договор'),
        ('civil_contract', 'Гражданско-правовой договор на выполнение работ (оказание услуг)')
    )

    TYPE_PERSON = (
        ('person_proxy', 'Человек, который подаёт документы по доверенности'),
        ('director', 'Директор')
    )

    worker_id = serializers.IntegerField(required=True)
    name_territorial_body = serializers.CharField(write_only=True, max_length=100)
    position = serializers.CharField(write_only=True, max_length=100)
    base = serializers.ChoiceField(choices=BASES)
    end_date = serializers.DateField(write_only=True)
    initiator = serializers.BooleanField()
    person = serializers.ChoiceField(choices=TYPE_PERSON)
    full_name = serializers.CharField(write_only=True, max_length=55)
    series = serializers.CharField(max_length=4)
    number = serializers.CharField(max_length=8)
    date_issue = serializers.DateField(write_only=True)
    issued_by = serializers.CharField(write_only=True, max_length=100)

    def validate_worker_id(self, value):
        if not Worker.objects.filter(pk=value).exists():
            raise CustomValidationError({'worker_id': 'Работника не существует'})

        user = self.context['request'].user.username
        list_organizations = []
        for organization in OrganizationUser.objects.filter(user_id=user):
            list_organizations.append(organization.organization_id)

        #Можно формировать бланки только для своих работников
        if Worker.objects.get(pk=value).organization_id not in list_organizations:
            raise CustomValidationError({'worker_id': 'Работника не из вашей организации'})

    def create(self, validated_data):
        return validated_data


class ShowManagersSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResponsiblePersons
        fields = '__all__'