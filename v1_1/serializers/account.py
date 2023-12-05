from django.contrib.auth.hashers import check_password
from django.contrib.auth import password_validation
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from v1_1.common_utils.token import get_token
from v1_1.models import User
from v1_1.common_utils.serializers import CharToStorageField


class AuthSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    redirect_url = serializers.CharField(read_only=True)

    @staticmethod
    def _get_user(validated_data):
        return User.objects.get(username=validated_data['username'])

    def validate(self, attrs):
        try:
            user = self._get_user(attrs)
            if not check_password(attrs.get('password'), user.password):
                raise ValidationError({'message': 'username_or_password_invalid'})
        except User.DoesNotExist:
            raise ValidationError({'message': 'username_or_password_invalid'})
        return attrs

    def create(self, validated_data):
        try:
            user = self._get_user(validated_data)
            token = get_token(self.context['request'], user)
            return {
                'access': str(token.access_token),
                'refresh': str(token)
            }
        except User.DoesNotExist:
            return {
                'redirect_url': f"{self.context['request'].scheme}://{self.context['request'].get_host()}"
                                f"/UMS/api/v1.0/account/create/"
            }


class AccountCreateSerializer(serializers.ModelSerializer):
    """ User's registering serializer. """
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    verified_password = serializers.CharField(write_only=True, required=True)
    name = serializers.CharField(required=True)
    surname = serializers.CharField(required=True)
    lastname = serializers.CharField()

    class Meta:
        model = User
        fields = (
            'username',
            'password',
            'verified_password',
            'name',
            "surname",
            'lastname'
        )

    @staticmethod
    def validate_username(value):
        if User.objects.filter(username=value).exists():
            raise ValidationError({'username': 'username_already_has'})
        return value

    @staticmethod
    def validate_password(value):
        try:
            password_validation.validate_password(value)
        except ValidationError as e:
            raise ValidationError({'password': e})
        return value

    def create(self, validated_data):
        if validated_data['verified_password'] != validated_data['password']:
            raise ValidationError({'verified_password': 'passwords_do_not_match'})
        validated_data.pop('verified_password')
        instance: User = super(AccountCreateSerializer, self).create(validated_data)
        instance.set_password(validated_data['password'])
        instance.save()
        return instance


class AccountDetailSerializer(serializers.ModelSerializer):
    avatar = CharToStorageField(read_only=True, source='image_avatar')

    class Meta:
        model = User
        fields = (
            'username', 'name', 'surname', 'lastname', 'phone', 'birthday',
            'avatar'
        )