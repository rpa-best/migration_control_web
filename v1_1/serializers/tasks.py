from rest_framework import serializers
from v1_1.models.worker import DocumentsWorker, Worker
from datetime import date, datetime, timedelta


class TaskDocuments(serializers.ModelSerializer):
    days_until_expiration = serializers.SerializerMethodField()
    recommended_start_date = serializers.SerializerMethodField()
    document = serializers.SerializerMethodField()
    worker = serializers.SerializerMethodField()

    class Meta:
        model = DocumentsWorker
        fields = '__all__'

    def get_document(self, obj):
        return obj.get_type_document_display()

    def get_days_until_expiration(self, obj):
        today = date.today()
        if obj.date_end <= today:
            return 'Просрочено'
        else:
            return (obj.date_end - today).days

    def get_recommended_start_date(self, obj):
        return obj.date_end - timedelta(days=7)

    def get_worker(self, obj):
        worker_id = obj.worker_id.id
        # ФИО работника
        name_worker = Worker.objects.get(pk=obj.worker_id.id).name
        surname_worker = Worker.objects.get(pk=worker_id).surname
        patronymic_worker = Worker.objects.get(pk=worker_id).patronymic

        full_name_worker = f'{surname_worker} {name_worker}'
        if patronymic_worker:
            full_name_worker += f' {patronymic_worker}'

        return full_name_worker


class TaskInfo(serializers.Serializer):
    days_until_expiration = serializers.CharField()
    recommended_start_date = serializers.DateField()


class NumberSerializer(serializers.Serializer):
    number = serializers.IntegerField(read_only=True)

class DocumentsWorkerSerializer(serializers.ModelSerializer):
    days_until_expiration = serializers.SerializerMethodField()

    class Meta:
        model = DocumentsWorker
        fields = '__all__'

    def get_days_until_expiration(self, obj):
        today = date.today()
        print(today)
        print(obj.date_end)
        if obj.date_end <= today:
            return 'Просрочено'
        else:
            return (obj.date_end - today).days