from django.urls import include, path
from rest_framework import routers
from v1_1.views.blanks import NoticeConclusionAPIView, EmploymentContractAPIView, SuspensionOrderAPIView, \
    PaymentOrderAPIView, ContractProvisionPaidServicesAPIView, SearchWorkers


router = routers.DefaultRouter()
router.register('search-workers/', SearchWorkers, 'search_workers')

urlpatterns = [
    path('', include(router.urls)),
    path('employment-contract/', EmploymentContractAPIView.as_view()),
    path('suspension-order/', SuspensionOrderAPIView.as_view()),
    path('payment-order/', PaymentOrderAPIView.as_view()),
    path('contract-provision-paid-services/', ContractProvisionPaidServicesAPIView.as_view()),
    path('notice-conclusion/', NoticeConclusionAPIView.as_view()),
]