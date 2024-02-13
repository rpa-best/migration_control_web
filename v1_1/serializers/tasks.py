from rest_framework import serializers

from v1_1.models.worker import DocumentsWorker


class DocumentsWorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentsWorker
        fields = '__all__'