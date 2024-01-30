from django.urls import include, path
from rest_framework import routers
from v1_1.views.worker import CreateAndUpdateWorkerAPIViewSet, DocumentsWorkerAPIViewSet, ShowWorkersAPIViewSet, \
    FileDocumentsAPIViewSet

router = routers.DefaultRouter()
router.register('worker', CreateAndUpdateWorkerAPIViewSet, 'worker')
router.register(r'(?P<organization>\d+)/worker', ShowWorkersAPIViewSet, 'list-worker')
router.register(r'(?P<worker_id>\d+)/document', DocumentsWorkerAPIViewSet, 'worker-documents'),
router.register(r'(?P<document_id>\d+)/file-document', FileDocumentsAPIViewSet, 'file-document'),

urlpatterns = [
    path('', include(router.urls)),
]