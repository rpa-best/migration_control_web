from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from v1_1.models.organization import Organization, MigrationAddress
from v1_1.serializers.organization import OrganizationCreateSerializer, OrganizationShowSerializer, \
    OrganizationPutAndPatchSerializer, MigrationAddressSerializer, MigrationAddressShowSerializer


@extend_schema(tags=['Organization'])
class OrganizationAPIViewSet(ModelViewSet):
    # queryset = Organization.objects.all()
    permission_class = IsAuthenticated

    def get_queryset(self):
        # Getting an authorized user
        user = self.request.user
        #Return only those organizations of which the user is an employee
        return Organization.objects.filter(organizationuser__user=user)

    def get_serializer_class(self):
        if self.request.method in ['POST']:
            serializer_class = OrganizationCreateSerializer
        elif self.request.method in ['PUT', 'PATCH']:
            serializer_class = OrganizationPutAndPatchSerializer
        else:
            serializer_class = OrganizationShowSerializer
        return serializer_class


@extend_schema(tags=['Migration addresses of organizations'])
class MigrationAddressAPIViewSet(ModelViewSet):
    permission_class = IsAuthenticated

    def get_queryset(self):
        # Getting an authorized user
        user = self.request.user
        #Return only those migration addresses with organizations of which the user is an employee
        return MigrationAddress.objects.filter(organization__organizationuser__user=user)

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            serializer_class = MigrationAddressShowSerializer
        else:
            serializer_class = MigrationAddressSerializer

        return serializer_class