from rest_framework import serializers
from v1_1.common_utils.custom_handler import CustomValidationError
from v1_1.models import OrganizationUser
from v1_1.models.worker import Worker


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
    end_date_urgent = serializers.DateField()
    start_time = serializers.TimeField(write_only=True)
    end_time = serializers.TimeField(write_only=True)
    cause = serializers.CharField()

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


# Платёжное поручение
class GenerationPaymentOrderSerializer(serializers.Serializer):
    worker_id = serializers.IntegerField(required=True)
    number_months = serializers.IntegerField(write_only=True, required=True)

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


class ContractProvisionPaidServicesSerializer(serializers.Serializer):
    worker_id = serializers.IntegerField(required=True)
    number = serializers.CharField(write_only=True, max_length=10, required=True)
    start_date = serializers.DateField(write_only=True, required=True)
    end_date = serializers.DateField(write_only=True, required=True)
    address = serializers.CharField(write_only=True, max_length=50, required=True)
    name_service = serializers.CharField(write_only=True, max_length=50, required=True)
    price = serializers.IntegerField(write_only=True, required=True)

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
    date_issue = serializers.DateField()
    issued_by = serializers.CharField(max_length=100)

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
