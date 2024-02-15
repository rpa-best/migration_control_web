from rest_framework import serializers
from v1_1.models.worker import DocumentsWorker


class TaskDocuments(serializers.ModelSerializer):
    class Meta:
        model = DocumentsWorker
        fields = '__all__'


class TaskInfo(serializers.Serializer):
    days_until_expiration = serializers.CharField()
    recommended_start_date = serializers.DateField()
