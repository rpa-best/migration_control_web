from rest_framework.generics import CreateAPIView

from v1_1.common_utils.generation_contract_provision_paid_services import GenerationContractProvisionPaidServices
from v1_1.common_utils.generation_employment_contract import GenerationEmploymentContractDocument
from v1_1.common_utils.generation_payment_order import GenerationPaymentOrder
from v1_1.common_utils.generation_suspension_order import GenerationSuspensionOrder
from v1_1.serializers.blanks import NoticeConclusionSerializer, EmploymentContractSerializer, \
    SuspensionOrderSerializer, GenerationPaymentOrderSerializer, ContractProvisionPaidServicesSerializer
from rest_framework.response import Response
from v1_1.swagger_content.blanks import blanks
import openpyxl
from django.http import HttpResponse


@blanks
class EmploymentContractAPIView(CreateAPIView):
    serializer_class = EmploymentContractSerializer

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return GenerationEmploymentContractDocument(request.data)


@blanks
class SuspensionOrderAPIView(CreateAPIView):
    serializer_class = SuspensionOrderSerializer

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return GenerationSuspensionOrder(request.data)


@blanks
class PaymentOrderAPIView(CreateAPIView):
    serializer_class = GenerationPaymentOrderSerializer

    def post(self, request,  **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return GenerationPaymentOrder(request.data)


@blanks
class ContractProvisionPaidServicesAPIView(CreateAPIView):
    serializer_class = ContractProvisionPaidServicesSerializer

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return GenerationContractProvisionPaidServices(request.data)


@blanks
class NoticeConclusionAPIView(CreateAPIView):
    serializer_class = NoticeConclusionSerializer

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # Создание и заполнение excel файла
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Notice Conclusion Data"

        row_num = 1
        for field_name, field_value in validated_data.items():
            col_num = 1
            ws.cell(row=row_num, column=col_num, value=field_name)
            col_num += 1
            ws.cell(row=row_num, column=col_num, value=field_value)
            row_num += 1

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="notice_conclusion_data.xlsx"'
        wb.save(response)
        return response
