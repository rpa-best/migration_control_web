from django.contrib.auth.hashers import check_password
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
