from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from v1_1.common_utils.custom_handler import CustomValidationError
from v1_1.models import OrganizationUser
from v1_1.models import DocumentsWorker, Worker, Tasks
from django.db.models import Q
from v1_1.serializers.worker import DocumentsWorkerSerializer
from v1_1.permissions.owner_or_admin import IsOwnerOrIsAdministratorInOrganizationWorker
from v1_1.serializers.tasks import (TaskDocuments, NumberSerializer, TasksSerializer,
                                    TasksStatusSerializer)
from drf_spectacular.utils import extend_schema
from rest_framework.generics import DestroyAPIView, UpdateAPIView


@extend_schema(tags=['Tasks'])
class ExpiringDocumentsView(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Список всех задач. Есть возможность искать задачи по определённому названию документа и фильтровать по статусу."""
    serializer_class = TaskDocuments
    permission_class = IsAuthenticated
    search_fields = ['type_document']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['type_document', 'worker_id__organization_id']

    def list(self, request, **kwargs):
        search_type_document = request.query_params.get('search', '')
        user = request.user  # Получение авторизованного пользователя

        try:
            organization_users = OrganizationUser.objects.filter(user=user)
            # Получение списка id организаций авторизованного пользователя
            organizations = [ou.organization.id for ou in organization_users]
        except OrganizationUser.DoesNotExist:
            return Response({'error': 'Вы не связаны ни с какой организацией'}, status=400)

        # Получение значений полей фильтрации из запроса GET
        type_document = request.query_params.get('type_document')
        worker_organization_id = request.query_params.get('worker_id__organization_id')
        status = request.query_params.get('status')

        # Необходимо, чтобы не возвращались документы у уволенных сотрудников
        filter_conditions = ~Q(worker_id__status='dismissed')

        # Фильтрация по типу документа
        if type_document:
            filter_conditions &= Q(document_id__type_document=type_document)
        else:
            filter_conditions &= Q(
                document_id__type_document__in=['passport', 'migration_card', 'registration', 'patent', 'paycheck',
                                                'temporary_residence', 'certificate_asylum', 'vmi_policy'])

        # Фильтрация по поисковому запросу
        if search_type_document:
            list_types_documents = [
                document[0] for document in DocumentsWorker.TYPES_DOCUMENTS
                if search_type_document.lower() in document[1].lower()
            ]
            if list_types_documents:
                filter_conditions &= Q(document_id__type_document__in=list_types_documents)

        # Фильтрация по организации работника
        if worker_organization_id:
            if not OrganizationUser.objects.filter(organization=worker_organization_id, user_id=user).exists():
                return Response({'error': 'Сотрудник не из вашей компании'}, status=400)
            filter_conditions &= Q(document_id__id__organization_id=worker_organization_id)
        else:
            filter_conditions &= Q(document_id__worker_id__organization_id__in=organizations)

        # Фильтрация по статусу
        if status:
            filter_conditions &= Q(status=status)

        tasks = Tasks.objects.filter(filter_conditions)

        page = self.paginate_queryset(tasks)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)


@extend_schema(tags=['Tasks'])
class WorkerExpiringDocumentsView(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Список задач для конкретного сотрудника"""
    serializer_class = TaskDocuments
    permission_class = IsAuthenticated

    def get_queryset(self):
        user = self.request.user

        worker_id = self.kwargs.get('worker_id')

        organization_id = Worker.objects.get(pk=worker_id).organization.id

        if not OrganizationUser.objects.filter(organization=organization_id, user=user).exists():
            raise CustomValidationError({'error': 'Данный сотрудник не из вашей компании'})

        filter_conditions = Q(document_id__worker_id=worker_id)

        queryset = Tasks.objects.filter(filter_conditions)

        return queryset


@extend_schema(tags=['Tasks'])
class ShowNumberTasksView(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Общее количество задач"""
    serializer_class = NumberSerializer
    permission_class = IsAuthenticated

    def list(self, request, **kwargs):
        user = self.request.user  # Получение авторизованного пользователя

        try:
            organization_users = OrganizationUser.objects.filter(user=user)
            # Получение списка id организаций авторизованного пользователя
            organizations = [ou.organization.id for ou in organization_users]
        except OrganizationUser.DoesNotExist:
            return Response({'error': 'Вы не связаны ни с какой организацией'}, status=400)

        # Необходимо, чтобы не возвращались документы у уволенных сотрудников
        filter_conditions = ~Q(document_id__worker_id__status='dismissed')

        filter_conditions &= Q(document_id__worker_id__organization_id__in=[org for org in organizations],
                              document_id__type_document__in=['passport', 'migration_card', 'registration', 'patent',
                                                              'paycheck', 'temporary_residence', 'certificate_asylum',
                                                              'vmi_policy'])

        number = Tasks.objects.filter(filter_conditions).count()

        return Response({'number': number})


@extend_schema(tags=['Tasks'])
class TaskDeleteView(DestroyAPIView):
    queryset = Tasks.objects.all()
    serializer_class = TasksSerializer


@extend_schema(tags=['Tasks'])
class TaskStatusUpdateView(UpdateAPIView):
    queryset = Tasks.objects.all()
    serializer_class = TasksStatusSerializer


@extend_schema(tags=['Tasks'])
class DocumentsWorkerTaskAPIViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = DocumentsWorkerSerializer
    permission_classes = [IsOwnerOrIsAdministratorInOrganizationWorker]

    def get_queryset(self):
        return DocumentsWorker.objects.filter(Q(worker_id=self.kwargs.get('worker_id')))

    def create(self, request, *args, **kwargs):
        id_old_doc = self.kwargs.get('doc_task_id')     # Получение документа из задачи,
        id_old_doc = DocumentsWorker.objects.get(pk=id_old_doc)
        id_old_doc.archive = True
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response_data = serializer.create(serializer.validated_data)  # Используем метод create из сериализатора
        id_old_doc.save()   # Сохранение занесения предыдущего документа из задачи в архив
        return Response(response_data)