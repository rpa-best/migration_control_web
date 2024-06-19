from rest_framework import serializers
from v1_1.common_utils.custom_handler import CustomValidationError
from v1_1.models.organization import OrganizationUser, ResponsiblePersons
from v1_1.models.worker import Worker, DocumentsWorker


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

        # Можно формировать бланки только для своих работников
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

        # Можно формировать бланки только для своих работников
        if Worker.objects.get(pk=value).organization_id not in list_organizations:
            raise CustomValidationError({'worker_id': 'Сотрудник не из вашей компании'})

    def validate_first_manager_id(self, value):
        if not ResponsiblePersons.objects.filter(pk=value).exists():
            raise CustomValidationError({'first_manager_id': 'Менеджера не существует'})

        user = self.context['request'].user.username
        list_organizations = []
        for organization in OrganizationUser.objects.filter(user_id=user):
            list_organizations.append(organization.organization_id)

        if ResponsiblePersons.objects.get(pk=value).organization.id not in list_organizations:
            raise CustomValidationError({'first_manager_id': 'Менеджер не из вашей компании'})

        return value

    def validate_second_manager_id(self, value):
        if not ResponsiblePersons.objects.filter(pk=value).exists():
            raise CustomValidationError({'second_manager_id': 'Менеджера не существует'})

        user = self.context['request'].user.username
        list_organizations = []
        for organization in OrganizationUser.objects.filter(user_id=user):
            list_organizations.append(organization.organization_id)

        if ResponsiblePersons.objects.get(pk=value).organization.id not in list_organizations:
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

        # Можно формировать бланки только для своих работников
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

        # Можно формировать бланки только для своих работников
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

        # Можно формировать бланки только для своих работников
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
    full_name = serializers.CharField(write_only=True, max_length=55, required=False)
    series = serializers.CharField(required=False)
    number = serializers.CharField(required=False)
    date_issue = serializers.DateField(write_only=True, required=False)
    issued_by = serializers.CharField(write_only=True, max_length=100, required=False)

    def validate_worker_id(self, value):
        if not Worker.objects.filter(pk=value).exists():
            raise CustomValidationError({'worker_id': 'Работника не существует'})

        user = self.context['request'].user.username
        list_organizations = []
        for organization in OrganizationUser.objects.filter(user_id=user):
            list_organizations.append(organization.organization_id)

        # Можно формировать бланки только для своих работников
        if Worker.objects.get(pk=value).organization_id not in list_organizations:
            raise CustomValidationError({'worker_id': 'Работника не из вашей организации'})

    def create(self, validated_data):
        return validated_data


class ArrivalNoticeSerializer(serializers.Serializer):
    TYPE_DOCUMENT = (
        ('not_documents', 'Нет документов'),
        ('visa', 'Виза'),
        ('resident_card', 'Вид на жительство'),
        ('temporary_residence_permit', 'Разрешение на временное проживание'),
        ('temporary_residence_permit', 'Разрешение на временное проживание в целях получения образования'),
    )

    TYPE_DEPARTURE = (
        ('tourism', 'Туризм'),
        ('business', 'Деловая'),
        ('studies', 'Учеба'),
        ('work', 'Работа'),
        ('private', 'Частная'),
        ('transit', 'Транзит'),
        ('humanitarian', 'Гуманитарная'),
        ('other', 'Иная')
    )

    TYPE_RECEIVING_SIDE = (
        ('legal_entity', 'Юридическое лицо'),
        ('individual', 'Физическое лицо')
    )

    IDENTIFICATION_CARD = (
        ('passport', 'Паспорт'),
        ('residence_permit', 'Вид на жительство'),
        ('certificate_asylum', 'Свидетельство о предоставлении убежища')
    )

    TYPE_PLACE_STAY = (
        ('residential_premises', 'Жилое помещение'),
        ('other_premises', 'Иное помещение'),
        ('organization', 'Организация')
    )

    worker_id = serializers.IntegerField(help_text='id сотрудника', required=True)
    # Первый лист
    document_type = serializers.ChoiceField(help_text='Тип документа', write_only=True, choices=TYPE_DOCUMENT)
    series = serializers.CharField(help_text='Серия документа', max_length=4)
    number = serializers.CharField(help_text='Номер документа', max_length=8)
    date_issue = serializers.DateField(help_text='Дата выдачи документа', write_only=True)
    validity_period = serializers.DateField(help_text='Дата окончания документа', write_only=True)
    purpose_departure = serializers.ChoiceField(help_text='Цель выезда', write_only=True, choices=TYPE_DEPARTURE)
    position = serializers.CharField(help_text='Профессия', write_only=True, max_length=100)
    duration_stay = serializers.DateField(help_text='Срок пребывания до', write_only=True)

    # Второй лист
    address_former_place_residence = serializers.CharField(help_text='Адрес прежнего места пребывания', max_length=255,
                                                           required=False)
    place_stay_region = serializers.CharField(help_text='Область, край, республика, автономный округ (область) места '
                                                        'пребывания', write_only=True, max_length=30)
    place_stay_area = serializers.CharField(help_text='Район места пребывания', write_only=True, max_length=30,
                                            required=False)
    place_stay_city = serializers.CharField(help_text='Город места пребывания', write_only=True, max_length=30)
    place_stay_street = serializers.CharField(help_text='Улица места пребывания', write_only=True, max_length=30)
    object_type = serializers.CharField(help_text='Тип объекта места пребывания (дом, участок, владение и иное)',
                                        max_length=20)
    place_stay_house = serializers.CharField(help_text='Дом места пребывания', write_only=True, max_length=4)
    place_stay_frame = serializers.CharField(help_text='Корпус места пребывания', max_length=5, required=False)
    place_stay_structure = serializers.CharField(help_text='Строение места пребывания', max_length=4)
    room_type = serializers.CharField(help_text='Тип комнаты места пребывания (квартира, комната, офис и иное)',
                                      max_length=25, required=False)
    place_stay_apartment = serializers.CharField(help_text='Квартира места пребывания', max_length=4, required=False)
    stated_period_stay = serializers.DateField(help_text='Заявленный срок пребывания до', write_only=True)
    place_stay = serializers.ChoiceField(help_text='Квартира, комната, офис и иное', write_only=True,
                                         choices=TYPE_PLACE_STAY)
    document_right_use = serializers.CharField(help_text='Наименование и реквизиты документа, подтверждающего право '
                                                         'пользования помещением (строением, сооружением) (указывается '
                                                         'при наличии)', max_length=63)

    # Третий лист
    receiving_side = serializers.ChoiceField(help_text='Принимающая сторона', choices=TYPE_RECEIVING_SIDE)
    surname_receiving_side = serializers.CharField(help_text='Фамилия принимающей стороны', max_length=50,
                                                   required=False)
    name_receiving_side = serializers.CharField(help_text='Имя принимающей стороны', max_length=50, required=False)
    patronymic_receiving_side = serializers.CharField(help_text='Отчество принимающей стороны', max_length=50,
                                                      required=False)
    type_of_identity_document = serializers.ChoiceField(help_text='Документ, удостоверяющий личность принимающей '
                                                                  'стороны', choices=IDENTIFICATION_CARD, required=False)
    series_receiving_side = serializers.CharField(help_text='Серия документа принимающей сторон', max_length=4,
                                                  required=False)
    number_receiving_side = serializers.CharField(help_text='Номер документа принимающей сторон', max_length=8,
                                                  required=False)
    date_issue_receiving_side = serializers.DateField(help_text='Дата выдачи документа принимающей сторон',
                                                      write_only=True, required=False)
    sell_by_receiving_side = serializers.DateField(help_text='Дата окончания документа принимающей стороны',
                                                   write_only=True, required=False)
    region = serializers.CharField(help_text='Область, край, республика, автономный округ (область) принимающей '
                                             'стороны', max_length=30, required=False)
    area = serializers.CharField(help_text='Район принимающей стороны', max_length=30, required=False)
    city = serializers.CharField(help_text='Город или другой населенный пункт принимающей стороны', max_length=30,
                                 required=False)
    street = serializers.CharField(help_text='Улица принимающей стороны', max_length=30, required=False)
    house = serializers.CharField(help_text='Дом принимающей стороны', max_length=4, required=False)
    frame = serializers.CharField(help_text='Корпус принимающей стороны', max_length=5, required=False, )
    structure = serializers.CharField(help_text='Строение принимающей стороны', max_length=4, required=False)
    apartment = serializers.CharField(help_text='Квартира принимающей стороны', max_length=4, required=False)

    def create(self, validated_data):
        return validated_data

class ShowManagersSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResponsiblePersons
        fields = '__all__'