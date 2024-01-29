from django.db.models import Q
from django.db.transaction import atomic
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from v1_1.api.bank_info import OrganizationSearch
from v1_1.common_utils.custom_handler import CustomValidationError
from v1_1.models.organization import Organization, MigrationAddress, OrganizationUser
from v1_1.permissions.owner import IsOwner
from v1_1.permissions.owner_or_admin import IsOwnerOrIsAdministratorInOrganization
from v1_1.serializers.organization import OrganizationCreateSerializer, OrganizationShowSerializer, \
    OrganizationPutAndPatchSerializer, MigrationAddressSerializer, MigrationAddressShowSerializer, \
    OrganizationCreateUserSerializer, ShowOrganizationUserSerializer, SearchOrganizationSerializer
from rest_framework import mixins, viewsets, status


@extend_schema(tags=['Organization'])
class OrganizationAPIViewSet(ModelViewSet):
    def get_queryset(self):
        # Получение авторизованного пользователя
        user = self.request.user
        #Возвращать только те организации, сотрудником которых является пользователь
        return Organization.objects.filter(organizationuser__user=user)

    def get_serializer_class(self):
        if self.request.method in ['POST']:
            serializer_class = OrganizationCreateSerializer
        elif self.request.method in ['PUT', 'PATCH']:
            serializer_class = OrganizationPutAndPatchSerializer
        else:
            serializer_class = OrganizationShowSerializer

        return serializer_class

    def get_permissions(self):
        # Определение разрешений в зависимости от типа запроса
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsOwner, ]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]


@extend_schema(tags=['Organization'], responses={'200': OrganizationCreateSerializer})
class SearchOrganizationAPIViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SearchOrganizationSerializer
    permission_class = IsOwner

    def list(self, request, **kwargs):
        # Получение ИНН или ОРГН из пути url
        inn_or_ogrn = self.kwargs.get('inn_or_ogrn')
        print(len(inn_or_ogrn))
        if inn_or_ogrn.isdigit():
            info = OrganizationSearch(inn_or_ogrn)
            if len(info) != 0:
                try:
                    organizational_form = info[0]['data']['opf']['short']
                    name_organization = info[0]['value']
                    inn = info[0]['data']['inn']
                    legal_address = info[0]['data']['address']['unrestricted_value']
                    actual_address = info[0]['data']['address']['unrestricted_value']
                    management = info[0]['data']['management']['name'].split()
                    name_director = ''
                    surname_director = ''
                    patronymic_director = ''

                    # Проверка количества слов в строке
                    if len(management) == 3:
                        surname_director = management[0]
                        name_director = management[1]
                        patronymic_director = management[2]
                    elif len(management) == 2:
                        if '-' in management[1]:
                            name_parts = management[1].split("-")
                            name_director = name_parts[0]
                            patronymic_director = name_parts[1]
                        else:
                            name_director = management[1]
                            patronymic_director = ""
                        surname_director = management[0]
                    elif len(management) == 4:
                        surname_director = management[0]
                        name_director = management[1] + '-' + management[2]
                        patronymic_director = management[3]

                    organization_data = {
                        'organizational_form': organizational_form,
                        'name_organization': name_organization,
                        'inn': inn,
                        'legal_address': legal_address,
                        'actual_address': actual_address,
                        'surname_director': surname_director,
                        'name_director': name_director,
                        'patronymic_director': patronymic_director
                    }
                    return Response(organization_data)

                except Exception:
                    raise CustomValidationError({'error': 'Компания не найдена'})
            else:
                raise CustomValidationError({'error': 'Компания не найдена'})
        else:
            raise CustomValidationError({'error': 'Некорректный ввод'})


@extend_schema(tags=['Migration addresses of organizations'])
class MigrationAddressAPIViewSet(ModelViewSet):
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

    def get_permissions(self):
        # Определение разрешений в зависимости от типа запроса
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrIsAdministratorInOrganization]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]


@extend_schema(tags=['Users of the organization'])
class OrganizationUsersListView(ModelViewSet):
    filterset_fields = ['role']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            serializer_class = OrganizationCreateUserSerializer
        else:
            serializer_class = ShowOrganizationUserSerializer

        return serializer_class

    def get_permissions(self):
        # Определение разрешений в зависимости от типа запроса
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrIsAdministratorInOrganization]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return OrganizationUser.objects.filter(Q(organization=self.kwargs.get('organization')))

    @atomic
    def create(self, request, *args, **kwargs):
        serializer = OrganizationCreateUserSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)