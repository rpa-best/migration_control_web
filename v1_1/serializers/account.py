from django.contrib.auth.hashers import check_password
from django.contrib.auth import password_validation
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from v1_1.common_utils.token import get_token
from v1_1.models import User


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
        # the password hash is set instead of the password itself (for security)
        instance.set_password(validated_data['password'])
        instance.save()
        return instance


class AccountPatchSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'username',
            'name',
            'surname',
            'lastname',
            'phone',
            'avatar',
            'birthday',
        )
        read_only_fields = ('username',)
        extra_kwargs = {
            'lang': {'write_only': True},
        }

    def update(self, instance, validated_data):
        updated_instance = super(AccountPatchSerializer, self).update(instance, validated_data)
        return updated_instance

    def get_avatar(self, instance):
        request = self.context.get('request')
        if instance.avatar:
            # Getting the path to the image
            image_path = instance.avatar.url
            # Building a complete absolute path to the image
            return request.build_absolute_uri(image_path)
        else:
            return None


class AccountDetailSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    def get_avatar(self, obj):
        if obj.avatar:
            return self.context['request'].build_absolute_uri(obj.avatar.url)
        return None

    class Meta:
        model = User
        fields = (
            'username', 'name', 'surname', 'lastname', 'phone', 'avatar', 'birthday'
        )


class UserAvatarsSerializer(serializers.ModelSerializer):
    """ User's avatars list serializer. """

    class Meta:
        model = User
        fields = ('avatar',)