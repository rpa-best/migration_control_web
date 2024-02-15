from rest_framework import mixins, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime, timedelta
from v1_1.models import OrganizationUser
from v1_1.models.worker import DocumentsWorker
from django.db.models import Q
from v1_1.serializers.tasks import DocumentsWorkerSerializer


class ExpiringDocumentsView(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = DocumentsWorkerSerializer
    permission_class = IsAuthenticated

    def list(self, request, **kwargs):
        user = request.user  # Получение авторизованного пользователя

        try:
            organization_users = OrganizationUser.objects.filter(user=user)
            # Получение списка id организаций авторизованного пользователя
            organizations = [ou.organization.id for ou in organization_users]
        except OrganizationUser.DoesNotExist:
            return Response({'error': 'Вы не связаны ни с какой организацией'}, status=400)

        # Текущая дата
        today = datetime.now().date()
        # Необходимо, чтобы возвращались документы, которым остаётся 30 дней до окончания срока или которые уже
        # просрочены
        expiring_documents = DocumentsWorker.objects.filter(
            Q(date_end__lte=today) | Q(date_end__gte=today, date_end__lte=today + timedelta(days=30)),
            type_document__in=['migration_card', 'patent', 'paycheck', 'temporary_residence', 'certificate_asylum'],
            worker_id__organization_id__in=[org for org in organizations]  # Фильтр по организациям пользователя
        )

        data = []
        for doc in expiring_documents:
            if doc.date_end <= today:
                days_until_expiration = 'Просрочено'
            else:
                days_until_expiration = (doc.date_end - today).days

            # Рекомендуемая дата начала оформления документа
            recommended_start_date = doc.date_end - timedelta(days=7)

            worker_info = {
                'document_id': doc.id,
                'document_type': doc.get_type_document_display(),
                'worker_id': doc.worker_id.id,
                'worker': f'{doc.worker_id.surname} {doc.worker_id.name} {doc.worker_id.patronymic or ''}',
                'organization_id': doc.worker_id.organization.id,
                'organization': f'{doc.worker_id.organization.get_organizational_form_display()} '
                                f'{doc.worker_id.organization.name}',
                'expiration_date': doc.date_end,
                'days_until_expiration': days_until_expiration,
                'recommended_start_date': recommended_start_date
            }
            data.append(worker_info)

        return Response(data)
