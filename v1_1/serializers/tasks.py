from rest_framework import serializers
from v1_1.models.worker import DocumentsWorker


class DocumentsWorkerSerializer(serializers.ModelSerializer):
    document_id = serializers.IntegerField()
    type_document = serializers.CharField()
    worker_id = serializers.IntegerField()
    worker = serializers.CharField()
    organization_id = serializers.IntegerField()
    organization = serializers.CharField()
    expiration_date = serializers.DateField()
    days_until_expiration = serializers.CharField()
    recommended_start_date = serializers.DateField()

    class Meta:
        model = DocumentsWorker
        fields = (
            'document_id',
            'type_document',
            'worker_id',
            'worker',
            'organization_id',
            'organization',
            'expiration_date',
            'days_until_expiration',
            'recommended_start_date'
        )