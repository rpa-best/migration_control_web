from rest_framework import serializers
from rest_framework_simplejwt.settings import api_settings
from v1_1.common_utils.file_paths import get_absolute_media_url_from_field
from v1_1.common_utils.token import get_token_class


# The class allows you to convert the value of a field into a representation.
class CharToStorageField(serializers.CharField):

    def to_representation(self, value):
        if not value:
            return None
        if value.startswith('http://') or value.startswith('https://'):
            return value
        return get_absolute_media_url_from_field(value)


class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField(read_only=True)

    def token_class(self):
        return get_token_class(self.context['request'])

    def validate(self, attrs):
        refresh = self.token_class()(attrs["refresh"])

        data = {"access": str(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    # Attempt to blacklist the given refresh token
                    refresh.blacklist()
                except AttributeError:
                    # If blacklist app not installed, `blacklist` method will
                    # not be present
                    pass

            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()

            data["refresh"] = str(refresh)

        return data