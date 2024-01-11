from drf_spectacular.utils import extend_schema
from rest_framework.viewsets import ModelViewSet
from v1_1.models.organization import OrganizationUser
from v1_1.models.worker import Worker
from v1_1.permissions.admin import IsAdministrator
from v1_1.permissions.observer import IsObserver
from v1_1.permissions.owner import IsOwner
from v1_1.serializers.worker import WorkerSerializer


@extend_schema(tags=['Worker'])
class WorkerAPIViewSet(ModelViewSet):
    serializer_class = WorkerSerializer

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
            permission_classes = [IsOwner, IsAdministrator]
        else:
            permission_classes = [IsOwner, IsAdministrator, IsObserver]

        return [permission() for permission in permission_classes]
