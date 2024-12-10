import copy
from django.db.transaction import atomic
from rest_framework import serializers
from v1_1.apies.DaData import AddressSearch
from v1_1.common_utils.custom_handler import CustomValidationError
from v1_1.models.organization import (Organization, MigrationAddress, OrganizationUser, DirectorOrganization,
                                      BookkeeperOrganization, HostPartyOrganization, ContactPersonOrganization,
                                      ResponsiblePersons, BodiesMIA, Bank)
from v1_1.models.subscription import Subscription, ServiceRate
from v1_1.models.user import User, HistoryPayment


class OrganizationShowSerializer(serializers.ModelSerializer):
    organizational_form = serializers.CharField(source='get_organizational_form_display')
    name_director = serializers.CharField(source='directororganization.name_director')
    surname_director = serializers.CharField(source='directororganization.surname_director')
    patronymic_director = serializers.CharField(source='directororganization.patronymic_director')
    passport_series = serializers.CharField(source='directororganization.passport_series')
    passport_number = serializers.CharField(source='directororganization.passport_number')
    issued_whom = serializers.CharField(source='directororganization.issued_whom')
    date_issue_passport = serializers.DateField(source='directororganization.date_issue_passport')
    date_end_passport = serializers.DateField(source='directororganization.date_end_passport')
    full_name_bookkeeper = serializers.DateField(source='bookkeeperorganization.full_name_bookkeeper')
    full_name_host_party = serializers.DateField(source='hostpartyorganization.full_name_host_party')
    phone_host_party = serializers.DateField(source='hostpartyorganization.phone_host_party')
    full_name_contact_person = serializers.DateField(source='contactpersonorganization.full_name')
    phone_contact_person = serializers.DateField(source='contactpersonorganization.phone')
    additional_phone = serializers.DateField(source='contactpersonorganization.additional_phone')
    email_contact_person = serializers.DateField(source='contactpersonorganization.email')

    class Meta:
        model = Organization
        fields = "__all__"


class OrganizationCreateSerializer(serializers.ModelSerializer):
    organizational_form = serializers.ChoiceField(choices=Organization.ORGANIZATIONAL_FORM)
    inn = serializers.CharField(max_length=20)
    legal_address = serializers.CharField()
    actual_address = serializers.CharField()
    name_director = serializers.CharField()
    surname_director = serializers.CharField()
    patronymic_director = serializers.CharField(required=False)

    class Meta:
        model = Organization
        fields = (
            'id',
            'organizational_form',
            'name',
            'inn',
            'legal_address',
            'actual_address',
            'name_director',
            'surname_director',
            'patronymic_director',
        )
        read_only_fields = ('id',)

    def validate_legal_address(self, value):
        if AddressSearch(value) is not None:
            return AddressSearch(value)
        return value

    def validate_actual_addresses(self, value):
        if AddressSearch(value) is not None:
            return AddressSearch(value)
        return value

    def validate_inn(self, value):
        if Organization.objects.filter(inn=value).exists():
            raise CustomValidationError({'inn': 'Организация с таким ИНН уже существует'})
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        # Проверка на наличие подписки
        subscription = Subscription.objects.filter(user=user, status='active').first()
        if not subscription:
            raise CustomValidationError({'message': 'У вас нет активной подписки.'})

        # Проверка на превышение лимита по количеству создаваемых организаций
        max_organizations = subscription.number_organizations
        current_organizations = Organization.objects.filter(owner=user).count()
        if current_organizations >= max_organizations:
            raise CustomValidationError({'message': 'Вы достигли максимального предела для создания организаций'})

        director = copy.deepcopy(validated_data)
        # Удаление директора из словаря, поскольку он не содержится в модели `DocumentsWorker`,
        # но есть в модели `DirectorOrganization`
        validated_data.pop('name_director', None)
        validated_data.pop('surname_director', None)
        validated_data.pop('patronymic_director', None)

        instance: Organization = super(OrganizationCreateSerializer, self).create(validated_data)
        instance.owner_id = self.context['request'].user
        instance.save()

        # При создании организации пользователь с подпиской заносится в список пользователей организации с правами
        # владельца
        OrganizationUser.objects.create(
            user=self.context['request'].user,
            organization=instance,
            role='owner'
        )

        DirectorOrganization.objects.create(
            organization=instance,
            name_director=director['name_director'],
            surname_director=director['surname_director'],
            patronymic_director=director['patronymic_director']
        )

        # Цена за создание организации
        price = subscription.service_rate.cost_organizations

        # Получение объекта пользователя
        user_obj = User.objects.get(username=user)

        if price > user_obj.balance:
            raise CustomValidationError({'message': 'Недостаточно средств на балансе'})

        # Обновление баланса пользователя
        user_obj.balance -= price
        user_obj.save()

        # Запись платежа за создание компании в историю
        HistoryPayment.objects.create(
            user=user,
            operation='Создание компании',
            amount=price
        )

        response_data = {
            'id': instance.id,
            'organizational_form': instance.organizational_form,
            'name': instance.name,
            'inn': instance.inn,
            'name_director': director['name_director'],
            'surname_director': director['surname_director'],
            'patronymic_director': director['patronymic_director'],
            'legal_address': instance.legal_address,
            'actual_address': instance.actual_address
        }

        return response_data


class OrganizationPutAndPatchSerializer(serializers.ModelSerializer):
    organizational_form = serializers.ChoiceField(choices=Organization.ORGANIZATIONAL_FORM, required=False)
    legal_address = serializers.CharField(required=False)
    inn = serializers.CharField(required=False)
    name_director = serializers.CharField(write_only=True, required=False)
    surname_director = serializers.CharField(write_only=True, required=False)
    patronymic_director = serializers.CharField(write_only=True, required=False)
    passport_series = serializers.CharField(write_only=True, required=False)
    passport_number = serializers.CharField(write_only=True, required=False)
    issued_whom = serializers.CharField(write_only=True, required=False)
    date_issue_passport = serializers.DateField(write_only=True, required=False)
    date_end_passport = serializers.DateField(write_only=True, required=False)
    full_name_bookkeeper = serializers.CharField(write_only=True, required=False)
    full_name_host_party = serializers.CharField(write_only=True, required=False)
    phone_host_party = serializers.CharField(write_only=True, required=False)
    full_name_contact_person = serializers.CharField(write_only=True, required=False)
    phone_contact_person = serializers.CharField(write_only=True, required=False)
    additional_phone = serializers.CharField(write_only=True, required=False)
    email_contact_person = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Organization
        fields = (
            'organizational_form',
            'name',
            'inn',
            'kpp',
            'ogrn',
            'okved',
            'phone',
            'legal_address',
            'actual_address',
            'actual_address',
            'name_director',
            'surname_director',
            'patronymic_director',
            'passport_series',
            'passport_number',
            'issued_whom',
            'date_issue_passport',
            'date_end_passport',
            'full_name_bookkeeper',
            'full_name_host_party',
            'phone_host_party',
            'full_name_contact_person',
            'phone_contact_person',
            'additional_phone',
            'email_contact_person'
        )

    def validate_legal_address(self, value):
        if AddressSearch(value) is not None:
            return AddressSearch(value)
        return value

    def validate_inn(self, value):
        organization_id = self.context['request'].parser_context['kwargs'].get('pk')
        if Organization.objects.filter(inn=value).exclude(id=organization_id).exists():
            raise CustomValidationError({'inn': 'Компания с таким ИНН уже существует'})
        return value

    def validate(self, data):
        user = self.context['request'].user.username
        # Только сотрудник этой организации может удалить организацию, принимая во внимание, что у него есть права\
        # сделать это
        if not Organization.objects.filter(organizationuser__user=user).exists():
            raise CustomValidationError({'message': 'Вы не являетесь сотрудником этой организации'})
        else:
            return data

    def update(self, instance, validated_data):
        director = {
            'name_director':  validated_data.pop('name_director', None),
            'surname_director': validated_data.pop('surname_director', None),
            'patronymic_director': validated_data.pop('patronymic_director', None),
            'passport_series': validated_data.pop('passport_series', None),
            'passport_number': validated_data.pop('passport_number', None),
            'issued_whom': validated_data.pop('issued_whom', None),
            'date_issue_passport': validated_data.pop('date_issue_passport', None),
            'date_end_passport': validated_data.pop('date_end_passport', None),
        }

        contact_person = {
            'full_name': validated_data.pop('full_name_contact_person', None),
            'phone': validated_data.pop('phone_contact_person', None),
            'additional_phone': validated_data.pop('additional_phone', None),
            'email': validated_data.pop('email_contact_person', None),
        }

        # Исключение полей с значением None из словаря director_fields
        director_fields = {key: value for key, value in director.items() if value is not None}

        full_name_bookkeeper = validated_data.pop('full_name_bookkeeper', None)

        host_party = {
            'full_name_host_party':  validated_data.pop('full_name_host_party', None),
            'phone_host_party': validated_data.pop('phone_host_party', None),
        }

        host_party_fields = {key: value for key, value in host_party.items() if value is not None}

        contact_person_fields = {key: value for key, value in contact_person.items() if value is not None}

        instance: Organization = super(OrganizationPutAndPatchSerializer, self).update(instance, validated_data)
        instance.save()

        # Есть ли уже у организации директор?
        if DirectorOrganization.objects.filter(organization=instance.id).exists():
            pk = DirectorOrganization.objects.filter(organization=instance.id).first().id
            # Обновление данных о директоре
            DirectorOrganization.objects.filter(id=pk).update(**director_fields)
        else:
            # Создание директора
            director_fields['organization'] = instance
            DirectorOrganization.objects.create(**director)

        validated_data.update(director)

        # Существует бухгалтер у организации?
        if BookkeeperOrganization.objects.filter(organization=instance.id).exists():
            # Заполнено ФИО для обновления бухгалтера?
            if full_name_bookkeeper:
                # Получение первичного ключа у бухгалтера
                pk = BookkeeperOrganization.objects.filter(organization=instance.id).first().id
                # Обновление ФИО бухгалтера
                BookkeeperOrganization.objects.filter(id=pk).update(full_name_bookkeeper=full_name_bookkeeper)
        else:
            BookkeeperOrganization.objects.create(organization=instance, full_name_bookkeeper=full_name_bookkeeper)

        # Существует принимающая сторона у организации?
        if HostPartyOrganization.objects.filter(organization=instance.id).exists():
            # Получение первичного ключа у принимающей стороны
            pk = HostPartyOrganization.objects.filter(organization=instance.id).first().id
            # Обновление данных у принимающей стороны
            HostPartyOrganization.objects.filter(id=pk).update(**host_party_fields)
        else:
            # Создание принимающей стороны у организации
            host_party_fields['organization'] = instance
            HostPartyOrganization.objects.create(**host_party_fields)

        # Существует контактное лицо в организации?
        if ContactPersonOrganization.objects.filter(organization=instance.id).exists():
            pk = ContactPersonOrganization.objects.filter(organization=instance.id).first().id
            # Обновление данных о директоре
            ContactPersonOrganization.objects.filter(id=pk).update(**contact_person_fields)
        else:
            # Создание контактного
            contact_person_fields['organization'] = instance
            ContactPersonOrganization.objects.create(**contact_person_fields)

        return validated_data


class ShowMigrationAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = MigrationAddress
        fields = '__all__'

    def validate_organization(self, value):
        user = self.context['request'].user.username
        # Можно добавить адрес миграции только для организации, в которой работает пользователь.
        if not OrganizationUser.objects.filter(organization=value, user=user).exists():
            raise CustomValidationError({'organization': 'Вы не являетесь сотрудником этой организации'})
        else:
            return value

    def validate(self, attrs):
        migration_address_id = self.context['request'].parser_context['kwargs'].get('pk')
        organization = MigrationAddress.objects.get(pk=migration_address_id).organization
        user = self.context['request'].user.username

        if not OrganizationUser.objects.filter(organization=organization, user=user).exists():
            raise CustomValidationError({'organization': 'Вы не являетесь сотрудником этой организации'})
        else:
            return attrs


class MigrationAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = MigrationAddress
        fields = '__all__'

    def validate_organization(self, value):
        user = self.context['request'].user.username
        # Можно добавить адрес миграции только для организации, в которой работает пользователь.
        if not OrganizationUser.objects.filter(organization=value, user=user).exists():
            raise CustomValidationError({'organization': 'Вы не являетесь сотрудником этой организации'})
        else:
            return value

    def validate_name(self, value):
        if AddressSearch(value) is not None:
            value = AddressSearch(value)

        return value


class OrganizationCreateUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    surname = serializers.CharField(source='user.surname')
    first_name = serializers.CharField(source='user.first_name')
    patronymic = serializers.CharField(source='user.patronymic', required=False)
    role = serializers.ChoiceField(choices=OrganizationUser.USER_ROLE_CHOICES)

    class Meta:
        model = OrganizationUser
        fields = ('username', 'surname', 'first_name', 'patronymic', 'organization', 'role')
        read_only_fields = ('organization', )

    def validate_username(self, value):
        organization_id = self.context['request'].parser_context['kwargs'].get('organization')
        if OrganizationUser.objects.filter(user=value, organization=organization_id).exists():
            raise CustomValidationError({'username': 'Пользователь с этой почтой уже есть в организации'})

        return value

    def validate_role(self, value):
        role_user = OrganizationUser.objects.filter(user=self.context['request'].user.username).first().role

        if value == 'owner':
            raise CustomValidationError({'role': 'Запрещено назначать роль владельца'})

        if role_user == 'admin' and value == 'admin':
            raise CustomValidationError({'error': 'У вас нет прав назначать роль администратора'})

        if role_user == 'observer':
            raise CustomValidationError({'error': 'У вас нет прав добавлять пользователей'})

        return value

    def validate(self, data):
        user = self.context['request'].user.username
        organization_id = self.context['request'].parser_context['kwargs'].get('organization')
        # Можно добавить только пользователя к организации, в которой работает авторизованный пользователь.
        if not OrganizationUser.objects.filter(organization=organization_id, user=user).exists():
            raise CustomValidationError({'organization': 'Вы не являетесь сотрудником этой организации'})
        return data

    @atomic
    def create(self, validated_data):
        user_fields = {
            'username': validated_data['user']['username'],
            'surname': validated_data['user']['first_name'],
            'first_name': validated_data['user']['first_name'],
        }

        if 'patronymic' in validated_data['user']:
            user_fields['patronymic'] = validated_data['user']['patronymic']

        role = validated_data['role']
        organization = self.context['request'].parser_context['kwargs'].get('organization')

        if not User.objects.filter(username=validated_data['user']['username']).exists():
            #Создание пользователя
            user = User.objects.create(**user_fields)
            try:
                user.regenerate_and_send_password()
            except Exception:
                raise CustomValidationError({'error': 'Ошибка при генерации пароля для пользователя. Возможно email '
                                                      'не существует'})

        else:
            user = User.objects.filter(username=validated_data['user']['username']).first()

        # Занесение созданного пользователя в выбранную организацию
        organization_user = OrganizationUser.objects.create(
            user=user,
            organization_id=organization,
            role=role
        )
        return organization_user


class ShowOrganizationUserSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(source='user.phone')
    first_name = serializers.CharField(source='user.first_name')
    surname = serializers.CharField(source='user.surname')
    patronymic = serializers.CharField(source='user.patronymic')

    class Meta:
        model = OrganizationUser
        fields = '__all__'


class SearchOrganizationSerializer(serializers.Serializer):
    inn_or_ogrn = serializers.CharField(write_only=True, required=True)


class ResponsiblePersonsSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True, required=False)
    surname = serializers.CharField(write_only=True, required=False)
    patronymic = serializers.CharField(write_only=True, required=False)
    passport_series = serializers.CharField(write_only=True, required=False)
    passport_number = serializers.CharField(write_only=True, required=False)
    issued_whom = serializers.CharField(write_only=True, required=False)
    date_issue_passport = serializers.DateField(write_only=True, required=False)

    class Meta:
        model = ResponsiblePersons
        fields = '__all__'

    def validate_organization(self, value):
        user = self.context['request'].user.username
        # Можно добавить ответственное лицо для организации, в которой работает пользователь.
        if not OrganizationUser.objects.filter(organization=value, user=user).exists():
            raise CustomValidationError({'organization': 'Вы не являетесь сотрудником этой организации'})
        else:
            return value


class BodiesMIASerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = BodiesMIA
        fields = '__all__'

    def validate_organization(self, value):
        user = self.context['request'].user.username
        # Можно добавить ответственное лицо для организации, в которой работает пользователь.
        if not OrganizationUser.objects.filter(organization=value, user=user).exists():
            raise CustomValidationError({'organization': 'Вы не являетесь сотрудником этой организации'})
        else:
            return value


class SearchBankSerializer(serializers.Serializer):
    bic = serializers.CharField(write_only=True, required=True)


class BankShowAndCreateSerializer(serializers.ModelSerializer):
    bic = serializers.CharField(write_only=True, required=False)
    name_bank = serializers.CharField(write_only=True, required=False)
    payment_account = serializers.CharField(write_only=True, required=False)
    correspondent_account = serializers.CharField(write_only=True, required=False)
    city_bank = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Bank
        fields = '__all__'
        read_only_fields = ('organization',)

    def validate(self, data):
        organization = self.context['request'].parser_context['kwargs'].get('organization')
        user = self.context['request'].user.username
        # Можно указывать только ту организацию, в которой работает пользователь.
        if not OrganizationUser.objects.filter(organization=organization, user=user).exists():
            raise CustomValidationError({'organization': 'Вы не являетесь сотрудником этой компании'})

        return data

    def create(self, validated_data):
        organization = self.context['request'].parser_context['kwargs'].get('organization')
        if Bank.objects.filter(organization=organization).exists():
            raise CustomValidationError({'error': 'У компании уже есть банк'})

        organization = Organization.objects.get(pk=organization)
        validated_data['organization'] = organization
        instance: Bank = super().create(validated_data)
        instance.save()
        return instance


class BankUpdateSerializer(serializers.ModelSerializer):
    bic = serializers.CharField(write_only=True, required=False)
    name_bank = serializers.CharField(write_only=True, required=False)
    payment_account = serializers.CharField(write_only=True, required=False)
    correspondent_account = serializers.CharField(write_only=True, required=False)
    city_bank = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Bank
        fields = '__all__'

    def validate_organization(self, value):
        user = self.context['request'].user.username
        # Можно указывать только ту организацию, в которой работает пользователь.
        if not OrganizationUser.objects.filter(organization=value, user=user).exists():
            raise CustomValidationError({'organization': 'Вы не являетесь сотрудником этой компании'})

        return value