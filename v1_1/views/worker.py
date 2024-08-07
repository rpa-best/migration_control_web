from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.views import APIView
from v1_1.common_utils.custom_handler import CustomValidationError
from v1_1.common_utils.renderers import XMLRender
from v1_1.common_utils.xml import json_to_xml
from v1_1.filters.worker import WorkerFilter
from v1_1.models.organization import OrganizationUser
from v1_1.models.worker import Worker, DocumentsWorker, FileDocuments
from v1_1.permissions.owner_or_admin import IsOwnerOrIsAdministratorInOrganization, \
    IsOwnerOrIsAdministratorInOrganizationWorker, IsOwnerOrIsAdministratorForFileDocument
from v1_1.serializers.worker import WorkerSerializer, CreateWorkerSerializer, DocumentsWorkerSerializer, \
    FileDocumentsSerializer
from rest_framework import mixins, viewsets
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
from io import BytesIO
from django.http import HttpResponse
import zipfile
import os
import requests
from ..common_utils.renderers import FileRenderer
from rest_framework.renderers import JSONRenderer
import io
from rest_framework.decorators import action


@extend_schema(tags=['Worker'])
class CreateWorkerAPIViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    def get_serializer_class(self):
        if self.action in ['create']:
            serializer_class = CreateWorkerSerializer
        else:
            serializer_class = WorkerSerializer

        return serializer_class

    def get_queryset(self):
        # Получение авторизованного пользователя
        user = self.request.user

        # Получение организаций, в которых работает пользователь
        organizations = OrganizationUser.objects.filter(user=user).values_list('organization', flat=True)

        # Фильтрация работников по организации
        queryset = Worker.objects.filter(organization__in=organizations)

        return queryset

    def get_permissions(self):
        # Определение разрешений в зависимости от типа запроса
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrIsAdministratorInOrganization]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]


@extend_schema(tags=['Worker'])
class UpdateWorkerAPIViewSet(mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = WorkerSerializer
    permission_class = IsOwnerOrIsAdministratorInOrganizationWorker

    def get_queryset(self):
        # Получение авторизованного пользователя
        user = self.request.user

        # Получение организаций, в которых работает пользователь
        organizations = OrganizationUser.objects.filter(user=user).values_list('organization', flat=True)

        # Фильтрация работников по организации
        queryset = Worker.objects.filter(organization__in=organizations)

        return queryset


@extend_schema(tags=['Worker'])
class ShowWorkersAPIViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    filterset_fields = ['status']
    serializer_class = WorkerSerializer
    permission_class = IsAuthenticated
    renderer_classes = (JSONRenderer, XMLRender)

    def get_queryset(self):
        # Получение авторизованного пользователя
        user = self.request.user

        # Получение организаций, в которых работает пользователь
        if not OrganizationUser.objects.filter(user=user, organization=self.kwargs.get('organization')).exists():
            raise CustomValidationError({'organization': 'Вы не являетесь работником этой организации'})

        # Фильтрация работников по организации
        queryset = Worker.objects.filter(Q(organization=self.kwargs.get('organization')))

        return queryset

    def list_xml(self, request, *args, **kwargs):
        workers = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(workers, many=True)
        xml = json_to_xml(serializer.data)
        return Response(xml)

    def list(self, request, *args, **kwargs):
        if request.query_params.get("format") == "xml":
            return self.list_xml(request, *args, **kwargs)
        return super().list(request, *args, **kwargs)


@extend_schema(tags=['Documents worker'])
class DocumentsWorkerAPIViewSet(ModelViewSet):
    serializer_class = DocumentsWorkerSerializer
    filterset_fields = ['archive']

    def get_queryset(self):
        return DocumentsWorker.objects.filter(Q(worker_id=self.kwargs.get('worker_id')))

    def get_permissions(self):
        # Определение разрешений в зависимости от типа запроса
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrIsAdministratorInOrganizationWorker]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response_data = serializer.create(serializer.validated_data)  # Используем метод create из сериализатора
        return Response(response_data)


@extend_schema(tags=['Documents worker'])
class FileDocumentsAPIViewSet(ModelViewSet):
    serializer_class = FileDocumentsSerializer
    renderer_classes = (JSONRenderer, FileRenderer)

    def get_queryset(self):
        return FileDocuments.objects.filter(Q(document_id=self.kwargs.get('document_id')))

    def get_permissions(self):
        # Определение разрешений в зависимости от типа запроса
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrIsAdministratorForFileDocument]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response_data = serializer.create(serializer.validated_data)
        return Response(response_data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # Проверяем, запрашивается ли ZIP архив
        if request.query_params.get("format") == "zip":
            files = [self.request.build_absolute_uri(file.file_document.url) for file in queryset]
            return Response(files)

        # Если не запрашивается ZIP архив, возвращаем JSON
        return super().list(request, *args, **kwargs)