from rest_framework import serializers
from v1_1.common_utils.file_paths import get_absolute_media_url_from_field


# The class allows you to convert the value of a field into a representation.
class CharToStorageField(serializers.CharField):

    def to_representation(self, value):
        if not value:
            return None
        if value.startswith('http://') or value.startswith('https://'):
            return value
        return get_absolute_media_url_from_field(value)