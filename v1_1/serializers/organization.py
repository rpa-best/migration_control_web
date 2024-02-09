import copy
from django.db.transaction import atomic
from rest_framework import serializers
from v1_1.apies.DaData import AddressSearch
from v1_1.common_utils.custom_handler import CustomValidationError
from v1_1.models.organization import Organization, MigrationAddress, OrganizationUser, DirectorOrganization
from v1_1.models.subscription import Subscription
from v1_1.models.user import User


class OrganizationShowSerializer(serializers.ModelSerializer):
    organizational_form = serializers.CharField(source='get_organizational_form_display')

    class Meta:
        model = Organization
        fields = "__all__"


# class DirectorOrganizationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = DirectorOrganization
#         fields = (
#             'name_director',
#             'surname_director',
#             'patronymic_director'
#         )


class OrganizationCreateSerializer(serializers.ModelSerializer):
    organizational_form = serializers.ChoiceField(choices=Organization.ORGANIZATIONAL_FORM)
    inn = serializers.CharField(max_length=20)
    legal_address = serializers.CharField()
    actual_addresses = serializers.ListField(child=serializers.CharField())
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
            'actual_addresses',
            'name_director',
            'surname_director',
            'patronymic_director',
        )
        read_only_fields = ('id',)

    def validate_legal_address(self, value):
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
        max_organizations = subscription.service_rate.number_companies
        current_organizations = Organization.objects.filter(owner=user).count()
        if current_organizations >= max_organizations:
            raise CustomValidationError({'message': 'Вы достигли максимального предела для создания организаций.'})

        director = copy.deepcopy(validated_data)
        # Удаление директора из словаря, поскольку он не содержится в модели `DocumentsWorker`,
        # но есть в модели `DirectorOrganization`
        validated_data.pop('name_director', None)
        validated_data.pop('surname_director', None)
        validated_data.pop('patronymic_director', None)

        # Создание записей для модели MigrationAddress
        # actual_addresses = validated_data.pop('actual_address', [])  # Получаем массив фактических адресов
        actual_addresses = validated_data.pop('actual_addresses')

        instance: Organization = super(OrganizationCreateSerializer, self).create(validated_data)
        instance.owner_id = self.context['request'].user
        instance.save()
        # User.objects.filter(id=self.context['request'].user.id).update(is_owner=True)
        # При создании организации пользователь с подпиской заносится в список пользователей организации с правами
        # владельца
        OrganizationUser.objects.create(
            user=self.context['request'].user,
            organization=instance,
            role='owner'
        )

        # Добавление фактических адресов
        for address in actual_addresses:
            MigrationAddress.objects.create(organization=instance, name=address)

        DirectorOrganization.objects.create(
            organization_id=instance,
            name_director=director['name_director'],
            surname_director=director['surname_director'],
            patronymic_director=director['patronymic_director']
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
            'actual_addresses': actual_addresses
        }

        return response_data


class OrganizationPutAndPatchSerializer(serializers.ModelSerializer):
    organizational_form = serializers.ChoiceField(choices=Organization.ORGANIZATIONAL_FORM)
    legal_address = serializers.CharField()

    class Meta:
        model = Organization
        fields = (
            'organizational_form',
            'name',
            'inn',
            'kpp',
            'ogrn',
            'phone',
            'legal_address',
        )

    def validate_legal_address(self, value):
        if AddressSearch(value) is not None:
            return AddressSearch(value)
        return value

    def validate_inn(self, value):
        if Organization.objects.filter(inn=value).exists():
            raise CustomValidationError({'inn': 'Организация с таким ИНН уже существует'})
        return value

    def validate(self, data):
        user = self.context['request'].user.username
        # Только сотрудник этой организации может удалить организацию, принимая во внимание, что у него есть права\
        # сделать это
        if not Organization.objects.filter(organizationuser__user=user).exists():
            raise CustomValidationError({'message': 'Вы не являетесь сотрудником этой организации'})
        else:
            return data


class MigrationAddressShowSerializer(serializers.ModelSerializer):
    organization = OrganizationShowSerializer()

    class Meta:
        model = MigrationAddress
        fields = '__all__'


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


class OrganizationCreateUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    name = serializers.CharField(source='user.name')
    role = serializers.ChoiceField(choices=OrganizationUser.USER_ROLE_CHOICES)

    class Meta:
        model = OrganizationUser
        fields = ('username', 'name', 'organization', 'role')
        read_only_fields = ('organization', )

    def validate_username(self, value):
        organization_id = self.context['request'].parser_context['kwargs'].get('organization_id')
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
        username = validated_data['user']['username']
        name = validated_data['user']['name']
        role = validated_data['role']
        organization = self.context['request'].parser_context['kwargs'].get('organization')

        if not User.objects.filter(username=username).exists():
            #Создание пользователя
            user = User.objects.create(username=username, name=name)
            try:
                user.regenerate_and_send_password()
            except Exception:
                raise CustomValidationError({'error': 'Ошибка при генерации пароля для пользователя. Возможно email '
                                                      'не существует'})

        else:
            user = User.objects.filter(username=username).first()

        # Занесение созданного пользователя в выбранную организацию
        organization_user = OrganizationUser.objects.create(
            user=user,
            organization_id=organization,
            role=role
        )
        return organization_user


class ShowOrganizationUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationUser
        fields = '__all__'


class SearchOrganizationSerializer(serializers.Serializer):
    inn_or_ogrn = serializers.CharField(write_only=True, required=True)