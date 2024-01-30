from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from v1_1.common_utils.custom_handler import CustomValidationError
from v1_1.filters.worker import WorkerFilter
from v1_1.models.organization import OrganizationUser
from v1_1.models.worker import Worker, DocumentsWorker, FileDocuments
from v1_1.permissions.owner_or_admin import IsOwnerOrIsAdministratorInOrganization, \
    IsOwnerOrIsAdministratorInOrganizationWorker, IsOwnerOrIsAdministratorForFileDocument
from v1_1.serializers.worker import WorkerSerializer, CreateWorkerSerializer, DocumentsWorkerSerializer, \
    FileDocumentsSerializer
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response


@extend_schema(tags=['Worker'])
class CreateAndUpdateWorkerAPIViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    def get_serializer_class(self):
        if self.action in ['create']:
            serializer_class = CreateWorkerSerializer
        else:
            serializer_class = WorkerSerializer

        return serializer_class

    def get_queryset(self):
        # Получение авторизованного пользователя
        user = self.request.user

        # Получение организаций, в которых работает пользователь
        organizations = OrganizationUser.objects.filter(user=user).values_list('organization', flat=True)

        # Фильтрация работников по организации
        queryset = Worker.objects.filter(organization__in=organizations)

        return queryset

    def get_permissions(self):
        # Определение разрешений в зависимости от типа запроса
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrIsAdministratorInOrganization]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]


@extend_schema(tags=['Worker'])
class ShowWorkersAPIViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    filterset_fields = ['status']
    serializer_class = WorkerSerializer
    permission_class = IsAuthenticated

    def get_queryset(self):
        # Получение авторизованного пользователя
        user = self.request.user

        # Получение организаций, в которых работает пользователь
        if not OrganizationUser.objects.filter(user=user, organization=self.kwargs.get('organization')).exists():
            raise CustomValidationError({'organization': 'Вы не являетесь работником этой организации'})

        # Фильтрация работников по организации
        queryset = Worker.objects.filter(Q(organization=self.kwargs.get('organization')))

        return queryset


@extend_schema(tags=['Documents worker'])
class DocumentsWorkerAPIViewSet(ModelViewSet):
    serializer_class = DocumentsWorkerSerializer

    def get_queryset(self):
        return DocumentsWorker.objects.filter(Q(worker_id=self.kwargs.get('worker_id')))

    def get_permissions(self):
        # Определение разрешений в зависимости от типа запроса
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrIsAdministratorInOrganizationWorker]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response_data = serializer.create(serializer.validated_data)  # Используем метод create из сериализатора
        return Response(response_data)


@extend_schema(tags=['Documents worker'])
class FileDocumentsAPIViewSet(ModelViewSet):
    serializer_class = FileDocumentsSerializer

    def get_queryset(self):
        return FileDocuments.objects.filter(Q(document_id=self.kwargs.get('document_id')))

    def get_permissions(self):
        # Определение разрешений в зависимости от типа запроса
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrIsAdministratorForFileDocument]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response_data = serializer.create(serializer.validated_data)
        return Response(response_data)
