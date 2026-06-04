import mimetypes
import os

from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from v1_1.models import OrganizationUser
from v1_1.models.worker import FileDocuments


@api_view(['GET'])
@permission_classes([])
def protected_media(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    # Prevent path traversal
    media_root = os.path.realpath(settings.MEDIA_ROOT)
    real_path = os.path.realpath(file_path)
    if not real_path.startswith(media_root + os.sep):
        raise Http404

    if not os.path.isfile(real_path):
        raise Http404

    # Sensitive employee documents require auth + org membership
    file_doc = FileDocuments.objects.filter(file_document=path).first()
    if file_doc is not None:
        if not request.user.is_authenticated:
            raise Http404
        organization = file_doc.document_id.worker_id.organization
        user_in_org = OrganizationUser.objects.filter(
            user=request.user, organization=organization
        ).exists()
        if not user_in_org:
            raise Http404

    content_type, _ = mimetypes.guess_type(real_path)
    return FileResponse(open(real_path, 'rb'), content_type=content_type or 'application/octet-stream')
