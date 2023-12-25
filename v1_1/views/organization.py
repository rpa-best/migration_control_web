from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from v1_1.models.organization import Organization, MigrationAddress
from v1_1.permissions.admin import IsAdministrator
from v1_1.permissions.observer import IsObserver
from v1_1.permissions.owner import IsOwner
from v1_1.serializers.organization import OrganizationCreateSerializer, OrganizationShowSerializer, \
    OrganizationPutAndPatchSerializer, MigrationAddressSerializer, MigrationAddressShowSerializer


@extend_schema(tags=['Organization'])
class OrganizationAPIViewSet(ModelViewSet):
    def get_queryset(self):
        # Получение авторизованного пользователя
        user = self.request.user
        #Возвращать только те организации, сотрудником которых является пользователь
        return Organization.objects.filter(organizationuser__user=user)

    def get_serializer_class(self):
        #Создать организацию и обновить её данные можно только владелец подписки
        if self.request.method in ['POST']:
            serializer_class = OrganizationCreateSerializer
            # permission_class = IsOwner
        elif self.request.method in ['PUT', 'PATCH']:
            serializer_class = OrganizationPutAndPatchSerializer
            # permission_class = IsOwner
        else:
            serializer_class = OrganizationShowSerializer
            # permission_class = IsAuthenticated

        return serializer_class

    def get_permissions(self):
        # Определение разрешений в зависимости от типа запроса
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsOwner,]
        else:
            permission_classes = [IsOwner, IsAdministrator, IsObserver]

        return [permission() for permission in permission_classes]


@extend_schema(tags=['Migration addresses of organizations'])
class MigrationAddressAPIViewSet(ModelViewSet):
    permission_class = IsAuthenticated

    def get_queryset(self):
        # Получение авторизованного пользователя
        user = self.request.user
        #Возвращать только те адреса миграционого учета в организациях, сотрудником которых является пользователь
        return MigrationAddress.objects.filter(organization__organizationuser__user=user)

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            serializer_class = MigrationAddressShowSerializer
        else:
            serializer_class = MigrationAddressSerializer

        return serializer_class