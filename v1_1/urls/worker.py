from django.urls import include, path
from rest_framework import routers

from v1_1.views.account import ListServiceRateView
from v1_1.views.worker import CreateWorkerAPIViewSet, DocumentsWorkerAPIViewSet, ShowWorkersAPIViewSet, \
    FileDocumentsAPIViewSet, UpdateWorkerAPIViewSet, ListCountryView

router = routers.DefaultRouter()
router.register('create', CreateWorkerAPIViewSet, 'create-worker')
router.register('update', UpdateWorkerAPIViewSet, 'update-worker')
router.register(r'(?P<organization>\d+)/list', ShowWorkersAPIViewSet, 'list-worker')
router.register(r'(?P<worker_id>\d+)/document', DocumentsWorkerAPIViewSet, 'worker-documents'),
router.register(r'(?P<document_id>\d+)/file-document', FileDocumentsAPIViewSet, 'file-document'),

urlpatterns = [
    path('', include(router.urls)),
    path('list-country/', ListCountryView.as_view()),
]