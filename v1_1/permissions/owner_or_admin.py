from rest_framework.permissions import BasePermission
from v1_1.models.organization import OrganizationUser
from v1_1.models.subscription import Subscription, ServiceRate
from v1_1.models.worker import Worker, FileDocuments, DocumentsWorker
from django.db.models import Q


class IsOwnerOrIsAdministratorInOrganization(BasePermission):
    message = 'У Вас недостаточно прав. Необходимо быть владельцем или администратором'

    def has_permission(self, request, view):
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
            if request.data.get('worker_id') is not None:
                # Получение id работника из поля запроса
                worker_id = request.data.get('worker_id')
            elif request.query_params.get('worker_id') is not None:
                # Получение id работника из параметров запроса
                worker_id = request.query_params.get('worker_id')
            else:
                # Получение id работника из url пути
                worker_id = view.kwargs.get('worker_id')

            if Worker.objects.filter(pk=worker_id).exists():
                # Получение id организации работника
                organization = Worker.objects.filter(pk=worker_id).first().organization.id
                # Проверяем, является ли пользователь владельцем или администратором организации
                if OrganizationUser.objects.filter(user=request.user, organization=organization,
                                                   role='owner').exists() or \
                        OrganizationUser.objects.filter(user=request.user, organization=organization,
                                                        role='admin').exists():
                    # Получение владельца организации
                    owner = OrganizationUser.objects.filter(organization=organization, role='owner').first().user
                    # Проверка на любую активную подписку владельца (basic, standard или pro)
                    if Subscription.objects.filter(user=owner, status='active').exists():
                        return True
            else:
                return False
        else:
            return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


# Разрешение для взаимодействия с файлами документами работников
class IsOwnerOrIsAdministratorForFileDocument(BasePermission):
    message = 'У Вас недостаточно прав. Необходимо быть владельцем или администратором'

    def has_permission(self, request, view):

        if request.user.is_authenticated:
            # Проверка на существование документа
            if DocumentsWorker.objects.filter(pk=view.kwargs.get('document_id')).exists():
                # Получение id работника из документа
                worker_id = DocumentsWorker.objects.filter(pk=view.kwargs.get('document_id')).first().worker_id.id
                # Получение id организации работника
                organization = Worker.objects.filter(pk=worker_id).first().organization
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


# Разрешение Про подписки
class isPro(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.data.get('worker_id') is not None:
                # Получение id работника из поля запроса
                worker_id = request.data.get('worker_id')
            elif request.query_params.get('worker_id') is not None:
                # Получение id работника из параметров запроса
                worker_id = request.query_params.get('worker_id')
            else:
                # Получение id работника из url пути
                worker_id = view.kwargs.get('worker_id')

            if Worker.objects.filter(pk=worker_id).exists():
                # Получение id организации работника
                organization = Worker.objects.filter(pk=worker_id).first().organization.id
                # Проверяем, является ли пользователь владельцем или администратором организации
                if OrganizationUser.objects.filter(user=request.user, organization=organization,
                                                   role='owner').exists() or \
                        OrganizationUser.objects.filter(user=request.user, organization=organization,
                                                        role='admin').exists():
                    # Получение владельца организации
                    owner = OrganizationUser.objects.filter(organization=organization, role='owner').first().user
                    # Проверка на активную Про-подписку владельца
                    pro_rate = ServiceRate.objects.filter(type_tariff='pro').first()
                    if pro_rate and Subscription.objects.filter(
                            user=owner, status='active', service_rate=pro_rate).exists():
                        return True
            else:
                return False
        else:
            return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)