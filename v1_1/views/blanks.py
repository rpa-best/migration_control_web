from rest_framework.generics import CreateAPIView
from v1_1.common_utils.generation_contract_provision_paid_services import GenerationContractProvisionPaidServices
from v1_1.common_utils.generation_employment_contract import GenerationEmploymentContractDocument
from v1_1.common_utils.generation_notice_conclusion import GenerationNoticeConclusion
from v1_1.common_utils.generation_payment_order import GenerationPaymentOrder
from v1_1.common_utils.generation_suspension_order import GenerationSuspensionOrder
from v1_1.serializers.blanks import NoticeConclusionSerializer, EmploymentContractSerializer, \
    SuspensionOrderSerializer, GenerationPaymentOrderSerializer, ContractProvisionPaidServicesSerializer
from rest_framework.response import Response
from v1_1.swagger_content.blanks import blanks
import openpyxl
from django.http import HttpResponse
from v1_1.permissions.owner_or_admin import IsOwnerOrIsAdministratorInOrganizationWorker, isPro


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
    permission_classes = (isPro,)

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return GenerationNoticeConclusion(request.data)
