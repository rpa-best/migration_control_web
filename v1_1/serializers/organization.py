from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from v1_1.models.organization import Organization, MigrationAddress, OrganizationUser
from v1_1.models.subscription import Subscription
from v1_1.models.user import User


class OrganizationShowSerializer(serializers.ModelSerializer):
    organizational_form = serializers.CharField(source='get_organizational_form_display')

    class Meta:
        model = Organization
        fields = "__all__"


class OrganizationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = (
            'organizational_form',
            'name',
            'inn',
            'kpp',
            'name_director',
            "surname_director",
            'lastname_director',
            'legal_address',
            'actual_address'
        )

    def create(self, validated_data):
        user = self.context['request'].user
        # Проверка на наличие подписки
        subscription = Subscription.objects.filter(user=user, status='active').first()
        if not subscription:
            raise ValidationError({'message': 'У вас нет активной подписки.'})

        # Проверка на превышение лимита по количеству создаваемых организаций
        max_organizations = subscription.service_rate.number_companies
        current_organizations = Organization.objects.filter(owner=user).count()
        if current_organizations >= max_organizations:
            raise ValidationError({'message': 'Вы достигли максимального предела для создания организаций.'})

        instance: Organization = super(OrganizationCreateSerializer, self).create(validated_data)
        instance.owner_id = self.context['request'].user
        instance.save()
        User.objects.filter(id=self.context['request'].user.id).update(is_owner=True)
        # При создании организации пользователь с подпиской заносится в список пользователей организации с правами
        # владельца
        OrganizationUser.objects.create(
            user=self.context['request'].user,
            organization=instance,
            role='owner'
        )
        return instance


class OrganizationPutAndPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = (
            'name',
            'organizational_form',
            'inn',
            'kpp',
            'ogrn',
            'name_director',
            "surname_director",
            'lastname_director',
            'legal_address',
            'actual_address'
        )

    def validate(self, data):
        user = self.context['request'].user.username
        # Только сотрудник этой организации может удалить организацию, принимая во внимание, что у него есть права\
        # сделать это
        if not Organization.objects.filter(organizationuser__user=user).exists():
            raise ValidationError({'message': 'Вы не являетесь сотрудником этой организации'})
        else:
            return data


class MigrationAddressShowSerializer(serializers.ModelSerializer):
    organization = OrganizationShowSerializer()

    class Meta:
        model = MigrationAddress
        fields = "__all__"


class MigrationAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = MigrationAddress
        fields = "__all__"

    def validate_organization(self, value):
        user = self.context['request'].user.username
        # Можно добавить адрес миграции только для организации, в которой работает пользователь.
        if not OrganizationUser.objects.filter(organization=value, user_id=user).exists():
            raise ValidationError({'message': 'Вы не являетесь сотрудником этой организации'})
        else:
            return value


