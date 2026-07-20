from rest_framework.generics import CreateAPIView, ListAPIView
from v1_1.common_utils.generation_contract_provision_paid_services import GenerationContractProvisionPaidServices
from v1_1.common_utils.generation_employment_contract import GenerationEmploymentContractDocument
from v1_1.common_utils.generation_notice_conclusion import GenerationNoticeConclusion
from v1_1.common_utils.generation_payment_order import GenerationPaymentOrder
from v1_1.common_utils.generation_suspension_order import GenerationSuspensionOrder
from v1_1.common_utils.generation_notice_termination import GenerationNoticeTermination
from v1_1.common_utils.generation_arrival_notice import GenerationArrivalNotice
from v1_1.serializers.blanks import (NoticeConclusionSerializer, EmploymentContractSerializer,
                                     SuspensionOrderSerializer, GenerationPaymentOrderSerializer,
                                     ContractProvisionPaidServicesSerializer, SearchWorkerSerializer,
                                     ShowManagersSerializer, NoticeTerminationSerializer, ArrivalNoticeSerializer)
from rest_framework.response import Response
from v1_1.swagger_content.blanks import blanks, search_worker, managers
from v1_1.permissions.owner_or_admin import IsOwnerOrIsAdministratorInOrganizationWorker, isPro
from rest_framework import mixins, viewsets
from ..common_utils.custom_handler import CustomValidationError
from ..models import Worker, DocumentsWorker
from ..models import Organization, OrganizationUser, ResponsiblePersons
from django.db.models import Q


@search_worker
class SearchWorkers(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SearchWorkerSerializer

    def list(self, request, *args, **kwargs):
        search = request.query_params.get('search', '')
        search_parts = search.split()

        # Получение авторизованного пользователя
        user = self.request.user

        # Получение организаций, в которых работает пользователь, чтобы результат поиска выдавал только своих
        # сотрудников
        organizations = OrganizationUser.objects.filter(user=user).values_list('organization', flat=True)

        q_objects = Q()
        for search_part in search_parts:
            q_objects &= (Q(name__icontains=search_part) |
                          Q(surname__icontains=search_part) |
                          Q(patronymic__icontains=search_part))

        workers = Worker.objects.filter(q_objects,  organization__in=organizations)
        results = []
        for worker in workers:
            documents = DocumentsWorker.objects.filter(worker_id=worker)
            organization = Organization.objects.get(pk=worker.organization_id)
            inn = documents.filter(type_document='INN').first().number if documents.filter(
                type_document='INN').exists() else ''

            result_str = (f'{worker.surname} {worker.name} {worker.patronymic} (ИНН: {inn}) '
                          f'{organization.get_organizational_form_display()} "{organization.name}"')
            results.append({
                'organization_id': organization.id,
                'worker_id': worker.id,
                'worker': result_str,
                'date_employment': worker.date_employment,
                'position': worker.position,
            })

        return Response(results)


@blanks
class EmploymentContractAPIView(CreateAPIView):
    serializer_class = EmploymentContractSerializer
    permission_classes = (IsOwnerOrIsAdministratorInOrganizationWorker,)

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return GenerationEmploymentContractDocument(request.data)


@blanks
class SuspensionOrderAPIView(CreateAPIView):
    serializer_class = SuspensionOrderSerializer
    permission_classes = (IsOwnerOrIsAdministratorInOrganizationWorker,)

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return GenerationSuspensionOrder(request.data)


@blanks
class PaymentOrderAPIView(CreateAPIView):
    serializer_class = GenerationPaymentOrderSerializer
    permission_classes = (IsOwnerOrIsAdministratorInOrganizationWorker,)

    def post(self, request,  **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return GenerationPaymentOrder(request.data)


@blanks
class ContractProvisionPaidServicesAPIView(CreateAPIView):
    serializer_class = ContractProvisionPaidServicesSerializer
    permission_classes = (IsOwnerOrIsAdministratorInOrganizationWorker,)

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return GenerationContractProvisionPaidServices(request.data)


@blanks
class NoticeConclusionAPIView(CreateAPIView):
    serializer_class = NoticeConclusionSerializer
    permission_classes = (IsOwnerOrIsAdministratorInOrganizationWorker,)

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return GenerationNoticeConclusion(request.data)


@blanks
class NoticeTerminationAPIView(CreateAPIView):
    serializer_class = NoticeTerminationSerializer
    permission_classes = (IsOwnerOrIsAdministratorInOrganizationWorker,)

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return GenerationNoticeTermination(request.data)


@blanks
class ArrivalNoticeAPIView(CreateAPIView):
    serializer_class = ArrivalNoticeSerializer
    permission_classes = (IsOwnerOrIsAdministratorInOrganizationWorker,)

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return GenerationArrivalNotice(request.data)


@managers
class ShowManagersAPIView(ListAPIView):
    serializer_class = ShowManagersSerializer

    def list(self, request, **kwargs):
        # Получение авторизованного пользователя
        user = self.request.user

        # Получение организаций, в которых работает пользователь
        if not OrganizationUser.objects.filter(user=user, organization=self.kwargs.get('organization')).exists():
            raise CustomValidationError({'organization': 'Вы не являетесь работником этой организации'})

        result = []
        # Фильтрация менеджеров по организации
        managers = ResponsiblePersons.objects.filter(Q(organization=self.kwargs.get('organization')))

        for manager in managers:
            full_name = f'{manager.surname} {manager.name}'
            if manager.patronymic:
                full_name += f' {manager.patronymic}'

            result.append({
                'manager_id': manager.id,
                'full_name': full_name
            })

        return Response(result)

