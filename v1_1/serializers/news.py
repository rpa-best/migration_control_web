from rest_framework import serializers
from v1_1.common_utils.custom_handler import CustomValidationError
from ..models.news import News, TagsNew, Tags
from ..models.user import User


class TagsNewSerializer(serializers.ModelSerializer):
    tag_name = serializers.CharField(source='tag.name')

    class Meta:
        model = TagsNew
        fields = ('tag_name',)


class NewsSerializer(serializers.ModelSerializer):
    tags = TagsNewSerializer(source='tagsnew_set', many=True, read_only=True)
    content = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = '__all__'

    def get_content(self, obj):
        return obj.content[:30] + '...' if len(obj.content) > 30 else obj.content

    def get_author(self, obj):
        if obj.author:
            fullname_list = []

            if obj.author.surname:
                fullname_list.append(obj.author.surname)
            if obj.author.first_name:
                fullname_list.append(obj.author.first_name)
            if obj.author.patronymic:
                fullname_list.append(obj.author.patronymic)
            return ' '.join(fullname_list)
        return None


class NewsDetailSerializer(serializers.ModelSerializer):
    tags = TagsNewSerializer(source='tagsnew_set', many=True, read_only=True)
    author = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = '__all__'

    def get_author(self, obj):
        if obj.author:
            fullname_list = []

            if obj.author.surname:
                fullname_list.append(obj.author.surname)
            if obj.author.first_name:
                fullname_list.append(obj.author.first_name)
            if obj.author.patronymic:
                fullname_list.append(obj.author.patronymic)
            return ' '.join(fullname_list)
        return None