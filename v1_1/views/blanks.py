from rest_framework.generics import CreateAPIView
from v1_1.common_utils.generation_employment_contract import GenerationEmploymentContractDocument
from v1_1.common_utils.generation_suspension_order import GenerationSuspensionOrder
from v1_1.serializers.blanks import SerializersNoticeConclusion, SerializersEmploymentContract, \
    SerializersSuspensionOrder
from rest_framework.response import Response
from v1_1.swagger_content.blanks import blanks
import openpyxl
from django.http import HttpResponse


@blanks
class EmploymentContractAPIView(CreateAPIView):
    serializer_class = SerializersEmploymentContract

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return GenerationEmploymentContractDocument(request.data)


@blanks
class SuspensionOrderAPIView(CreateAPIView):
    serializer_class = SerializersSuspensionOrder

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return GenerationSuspensionOrder(request.data)


@blanks
class NoticeConclusionAPIView(CreateAPIView):
    serializer_class = SerializersNoticeConclusion

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
