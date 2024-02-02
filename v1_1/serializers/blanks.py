from rest_framework import serializers
from v1_1.common_utils.custom_handler import CustomValidationError


# Трудовой договор
class SerializersEmploymentContract(serializers.Serializer):
    CONTRACT_TYPE = (
        ('perpetual', 'Бессрочный договор'),
        ('urgent', 'Срочный договор')
    )

    worker_id = serializers.IntegerField()
    number = serializers.CharField(write_only=True, max_length=10)
    job_title = serializers.CharField(write_only=True, max_length=30)
    salary = serializers.IntegerField(write_only=True)
    contract_type = serializers.ChoiceField(choices=CONTRACT_TYPE)
    start_date = serializers.DateField(write_only=True)
    end_date_urgent = serializers.DateField()
    start_time = serializers.TimeField(write_only=True)
    end_time = serializers.TimeField(write_only=True)
    cause = serializers.CharField()

    def create(self, validated_data):
        return validated_data


# Уведомление о заключении
class SerializersNoticeConclusion(serializers.Serializer):
    BASE_TYPE_CHOICES = (
        ('employment_contract', 'Трудовой договор'),
        ('civil_contract', 'Гражданско-правовой договор на выполнение работ (оказание услуг)')
    )
    BASE_TYPE_PERSON = (
        ('person_proxy', 'Человек, который подаёт документы по доверенности'),
        ('director', 'Директор')
    )

    name_territorial_body = serializers.CharField(max_length=100)
    job_title = serializers.CharField(max_length=100)
    base = serializers.ChoiceField(choices=BASE_TYPE_CHOICES)
    start_date = serializers.DateField(write_only=True)
    address = serializers.CharField(max_length=100)
    person = serializers.ChoiceField(choices=BASE_TYPE_PERSON)
    full_name = serializers.CharField(max_length=55, required=False)
    series = serializers.CharField(required=False)
    number = serializers.CharField(required=False)
    date_issue = serializers.DateField()
    issued_by = serializers.CharField(max_length=100)

    def create(self, validated_data):
        return validated_data