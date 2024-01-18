from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from v1_1.models.organization import OrganizationUser
from v1_1.models.worker import Worker
from v1_1.permissions.owner_or_admin import IsOwnerOrIsAdministratorInOrganization
from v1_1.serializers.worker import WorkerSerializer, CreateWorkerSerializer


@extend_schema(tags=['Worker'])
class WorkerAPIViewSet(ModelViewSet):
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
