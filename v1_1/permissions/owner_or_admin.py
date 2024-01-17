from rest_framework.permissions import BasePermission
from v1_1.models.organization import OrganizationUser
from v1_1.models.subscription import Subscription


class IsOwnerOrIsAdministratorInOrganization(BasePermission):
    def has_permission(self, request, view):

        if request.data.get('organization') is not None:
            organization = request.data.get('organization')
        elif request.query_params.get('organization') is not None:
            organization = request.query_params.get('organization')
        else:
            organization = view.kwargs.get('organization')

        if request.user.is_authenticated:
            # Проверяем, является ли пользователь администратором организации
            if OrganizationUser.objects.filter(user=request.user, organization=organization, role='owner').exists() or\
            OrganizationUser.objects.filter(user=request.user, organization=organization, role='admin').exists():
                # Получение владельца организации
                owner = OrganizationUser.objects.filter(organization=organization, role='owner').first().user
                # Проверка на активную подписку владельца
                if Subscription.objects.filter(user=owner, status='active').exists():
                    return True
        return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)