from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from v1_1.models.organization import Organization, MigrationAddress, OrganizationUser
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
            'name_director',
            "surname_director",
            'lastname_director',
            'legal_address',
            'actual_address'
        )

    def create(self, validated_data):
        instance: Organization = super(OrganizationCreateSerializer, self).create(validated_data)
        instance.owner_id = self.context['request'].user
        instance.save()
        User.objects.filter(id=self.context['request'].user.id).update(is_owner=True)
        # When creating an organization, a user with a subscription is recorded in the list of users of the
        #organization with the rights of the owner
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
        #Only an employee of this organization can delete an organization, taking into account that he has the rights\
        # to do so
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
        #Can add a migration address only to the organization where the user works.
        if not OrganizationUser.objects.filter(organization=value, user_id=user).exists():
            raise ValidationError({'message': 'Вы не являетесь сотрудником этой организации'})
        else:
            return value


