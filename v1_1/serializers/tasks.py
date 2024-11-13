from rest_framework import serializers
from v1_1.models.worker import DocumentsWorker, Worker, Tasks
from datetime import date, datetime, timedelta


class TaskDocuments(serializers.ModelSerializer):
    organization_id = serializers.SerializerMethodField()
    organization = serializers.SerializerMethodField()
    document = serializers.SerializerMethodField()
    type_document = serializers.SerializerMethodField()
    date_end = serializers.SerializerMethodField()
    worker = serializers.SerializerMethodField()
    worker_id = serializers.SerializerMethodField()

    class Meta:
        model = Tasks
        fields = '__all__'

    def get_document(self, obj):
        return obj.document_id.get_type_document_display()

    def get_type_document(self, obj):
        return obj.document_id.type_document

    def get_date_end(self, obj):
        return obj.document_id.date_end

    def get_organization_id(self, obj):
        return obj.document_id.worker_id.organization.id

    def get_organization(self, obj):
        organization = (f'{obj.document_id.worker_id.organization.get_organizational_form_display()} '
                        f'{obj.document_id.worker_id.organization.name}')
        return organization

    def get_worker(self, obj):
        worker_id = obj.document_id.worker_id.id
        worker_obj = Worker.objects.get(pk=worker_id)
        # ФИО работника
        name_worker = worker_obj.name
        surname_worker = worker_obj.surname
        patronymic_worker = worker_obj.patronymic

        full_name_worker = f'{surname_worker} {name_worker}'
        if patronymic_worker:
            full_name_worker += f' {patronymic_worker}'

        return full_name_worker

    def get_worker_id(self, obj):
        worker_id = obj.document_id.worker_id.id
        return worker_id


class NumberSerializer(serializers.Serializer):
    number = serializers.IntegerField(read_only=True)


class DocumentsWorkerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tasks
        fields = '__all__'


class TasksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tasks
        fields = '__all__'


class TasksStatusSerializer(serializers.ModelSerializer):
    """Сериалайзер для изменения статуса задачи"""
    class Meta:
        model = Tasks
        fields = ['status']