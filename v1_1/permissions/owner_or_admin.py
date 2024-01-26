from rest_framework.permissions import BasePermission
from v1_1.models.organization import OrganizationUser
from v1_1.models.subscription import Subscription
from v1_1.models.worker import Worker


class IsOwnerOrIsAdministratorInOrganization(BasePermission):
    def has_permission(self, request, view):

        organization = None

        if request.data.get('organization') is not None:
            # Получение id организации из поля запроса
            organization = request.data.get('organization')
        elif request.query_params.get('organization') is not None:
            # Получение id организации из параметров запроса
            organization = request.query_params.get('organization')
        else:
            # Получение id организации из url пути
            organization = view.kwargs.get('organization')

        if request.user.is_authenticated:
            # Проверяем, является ли пользователь владельцем или администратором организации
            if (OrganizationUser.objects.filter(user=request.user, organization=organization, role='owner').exists() or
                    OrganizationUser.objects.filter(user=request.user, organization=organization, role='admin').exists()):
                # Получение владельца организации
                owner = OrganizationUser.objects.filter(organization=organization, role='owner').first().user
                # Проверка на активную подписку владельца
                if Subscription.objects.filter(user=owner, status='active').exists():
                    return True
        return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


# Разрешение для взаимодействия с работниками
class IsOwnerOrIsAdministratorInOrganizationWorker(BasePermission):
    def has_permission(self, request, view):

        if request.user.is_authenticated:
            if Worker.objects.filter(pk=view.kwargs.get('worker_id')).exists():
                # Получение id организации работника
                organization = Worker.objects.filter(pk=view.kwargs.get('worker_id')).first().organization.id
                # Проверяем, является ли пользователь владельцем или администратором организации
                if OrganizationUser.objects.filter(user=request.user, organization=organization,
                                                   role='owner').exists() or \
                        OrganizationUser.objects.filter(user=request.user, organization=organization,
                                                        role='admin').exists():
                    # Получение владельца организации
                    owner = OrganizationUser.objects.filter(organization=organization, role='owner').first().user
                    # Проверка на активную подписку владельца
                    if Subscription.objects.filter(user=owner, status='active').exists():
                        return True
            else:
                return False
        else:
            return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)