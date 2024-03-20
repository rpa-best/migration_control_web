from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime, timedelta
from v1_1.common_utils.custom_handler import CustomValidationError
from v1_1.models import OrganizationUser
from v1_1.models.worker import DocumentsWorker, Worker
from django.db.models import Q
from v1_1.serializers.tasks import TaskDocuments, TaskInfo, NumberSerializer
from drf_spectacular.utils import extend_schema


@extend_schema(tags=['Tasks'])
class ExpiringDocumentsView(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = TaskDocuments
    permission_class = IsAuthenticated
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type_document', 'worker_id__organization_id']

    def get_queryset(self):
        user = self.request.user

        try:
            organization_users = OrganizationUser.objects.filter(user=user)
            organizations = [ou.organization.id for ou in organization_users]
        except OrganizationUser.DoesNotExist:
            raise CustomValidationError({'error': 'Вы не связаны ни с какой организацией'}, status=400)

        # Текущая дата
        today = datetime.now().date()

        # Необходимо, чтобы возвращались документы, которым остаётся 30 дней до окончания срока или которые уже
        #     # просрочены
        filter_conditions = Q(date_end__lte=today) | Q(date_end__gte=today, date_end__lte=today + timedelta(days=30))

        # Получение значений полей фильтрации из запроса GET
        type_document = self.request.query_params.get('type_document')
        worker_organization_id = self.request.query_params.get('worker_id__organization_id')

        # Получение значений полей фильтрации из запроса GET
        if type_document:
            filter_conditions &= Q(type_document=type_document)
        else:
            filter_conditions &= Q(
                type_document__in=['migration_card', 'patent', 'paycheck', 'temporary_residence', 'certificate_asylum'])

        if worker_organization_id:
            if not OrganizationUser.objects.filter(organization=worker_organization_id, user_id=user).exists():
                raise CustomValidationError({'error': 'Вы не являетесь сотрудником этой организации'})
            filter_conditions &= Q(worker_id__organization_id=worker_organization_id)
        else:
            filter_conditions &= Q(worker_id__organization_id__in=[org for org in organizations])

        queryset = DocumentsWorker.objects.filter(filter_conditions)

        return queryset

    # def list(self, request, **kwargs):
    #     user = request.user  # Получение авторизованного пользователя
    #
    #     try:
    #         organization_users = OrganizationUser.objects.filter(user=user)
    #         # Получение списка id организаций авторизованного пользователя
    #         organizations = [ou.organization.id for ou in organization_users]
    #     except OrganizationUser.DoesNotExist:
    #         return Response({'error': 'Вы не связаны ни с какой организацией'}, status=400)
    #
    #     # Текущая дата
    #     today = datetime.now().date()
    #
    #     # Необходимо, чтобы возвращались документы, которым остаётся 30 дней до окончания срока или которые уже
    #     # просрочены
    #     filter_conditions = Q(date_end__lte=today) | Q(date_end__gte=today, date_end__lte=today + timedelta(days=30))
    #
    #     # Получение значений полей фильтрации из запроса GET
    #     type_document = request.query_params.get('type_document')
    #     worker_organization_id = request.query_params.get('worker_id__organization_id')
    #
    #     # Если значение поля type_document передано, добавляем его в условие фильтрации
    #     if type_document:
    #         filter_conditions &= Q(type_document=type_document)
    #     else:
    #         filter_conditions &= Q(type_document__in=['migration_card', 'patent', 'paycheck', 'temporary_residence', 'certificate_asylum'])
    #
    #     # Если значение поля worker_id__organization_id передано, добавляем его в условие фильтрации
    #     if worker_organization_id:
    #         if not OrganizationUser.objects.filter(organization=worker_organization_id, user_id=user).exists():
    #             raise CustomValidationError({'error': 'Вы не являетесь сотрудником этой организации'})
    #         filter_conditions &= Q(worker_id__organization_id=worker_organization_id)
    #     else:
    #         # Иначе список будет для всех организацией, в которых есть авторизованный пользователь
    #         filter_conditions &= Q(worker_id__organization_id__in=[org for org in organizations])
    #
    #     expiring_documents = DocumentsWorker.objects.filter(filter_conditions)
    #
    #     data = []
    #     for doc in expiring_documents:
    #         if doc.date_end <= today:
    #             days_until_expiration = 'Просрочено'
    #         else:
    #             # Количество оставшихся дней до окончания срока действия документа
    #             days_until_expiration = (doc.date_end - today).days
    #
    #         # Рекомендуемая дата начала оформления документа
    #         recommended_start_date = doc.date_end - timedelta(days=7)
    #
    #         worker_info = {
    #             'document_id': doc.id,
    #             'type_document': doc.get_type_document_display(),
    #             'worker_id': doc.worker_id.id,
    #             'worker': f'{doc.worker_id.surname} {doc.worker_id.name} {doc.worker_id.patronymic or ''}',
    #             'organization_id': doc.worker_id.organization.id,
    #             'organization': f'{doc.worker_id.organization.get_organizational_form_display()} '
    #                             f'{doc.worker_id.organization.name}',
    #             'expiration_date': doc.date_end,
    #             'days_until_expiration': days_until_expiration,
    #             'recommended_start_date': recommended_start_date
    #         }
    #         data.append(worker_info)
    #
    #     return Response(data)


@extend_schema(tags=['Tasks'])
class WorkerExpiringDocumentsView(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = TaskDocuments
    permission_class = IsAuthenticated

    def get_queryset(self):
        user = self.request.user

        worker_id = self.kwargs.get('worker_id')

        organization_id = Worker.objects.get(pk=worker_id).organization.id

        if not OrganizationUser.objects.filter(organization=organization_id, user=user).exists():
            raise CustomValidationError({'error': 'Данный сотрудник не из вашей компании'})

        filter_conditions = Q(worker_id=worker_id)

        today = datetime.now().date()

        filter_conditions &= Q(date_end__lte=today) | Q(date_end__gte=today, date_end__lte=today + timedelta(days=30))

        filter_conditions &= Q(
            type_document__in=['migration_card', 'patent', 'paycheck', 'temporary_residence', 'certificate_asylum'])

        queryset = DocumentsWorker.objects.filter(filter_conditions)

        return queryset


@extend_schema(tags=['Tasks'])
class TaskInfoView(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = TaskInfo
    permission_class = IsAuthenticated

    def list(self, request, **kwargs):
        # Получение авторизованного пользователя
        user = self.request.user

        worker_id = DocumentsWorker.objects.get(pk=self.kwargs.get('document_id')).worker_id.id
        organization_id = Worker.objects.get(pk=worker_id).organization.id

        if not OrganizationUser.objects.filter(organization=organization_id, user=user).exists():
            raise CustomValidationError({'error': 'Данный документ не принадлежит вашему сотруднику'})

        document = DocumentsWorker.objects.filter(pk=self.kwargs.get('document_id'))[0]

        # Текущая дата
        today = datetime.now().date()

        if document.date_end <= today:
            days_until_expiration = 'Просрочено'
            overdue = True
        else:
            # Количество оставшихся дней до окончания срока действия документа
            days_until_expiration = (document.date_end - today).days
            overdue = False

        # Рекомендуемая дата начала оформления документа
        recommended_start_date = document.date_end - timedelta(days=7)

        document_info = {
            'days_until_expiration': days_until_expiration,
            'recommended_start_date': recommended_start_date,
            'overdue': overdue
        }

        return Response(document_info)


@extend_schema(tags=['Tasks'])
class ShowNumberTasksView(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = NumberSerializer
    permission_class = IsAuthenticated

    def list(self, request, **kwargs):
        user = self.request.user

        try:
            organization_users = OrganizationUser.objects.filter(user=user)
            organizations = [ou.organization.id for ou in organization_users]
        except OrganizationUser.DoesNotExist:
            raise CustomValidationError({'error': 'Вы не связаны ни с какой организацией'}, status=400)

        # Текущая дата
        today = datetime.now().date()

        # Необходимо, чтобы возвращались документы, которым остаётся 30 дней до окончания срока или которые уже
        #     # просрочены
        filter_conditions = Q(date_end__lte=today) | Q(date_end__gte=today, date_end__lte=today + timedelta(days=30))

        # Получение значений полей фильтрации из запроса GET
        type_document = self.request.query_params.get('type_document')
        worker_organization_id = self.request.query_params.get('worker_id__organization_id')

        # Получение значений полей фильтрации из запроса GET
        if type_document:
            filter_conditions &= Q(type_document=type_document)
        else:
            filter_conditions &= Q(
                type_document__in=['migration_card', 'patent', 'paycheck', 'temporary_residence', 'certificate_asylum'])

        if worker_organization_id:
            if not OrganizationUser.objects.filter(organization=worker_organization_id, user_id=user).exists():
                raise CustomValidationError({'error': 'Вы не являетесь сотрудником этой организации'})
            filter_conditions &= Q(worker_id__organization_id=worker_organization_id)
        else:
            filter_conditions &= Q(worker_id__organization_id__in=[org for org in organizations])

        number = DocumentsWorker.objects.filter(filter_conditions).count()

        return Response({'number': number})