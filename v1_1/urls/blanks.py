from django.urls import path
from v1_1.views.blanks import NoticeConclusionAPIView, EmploymentContractAPIView, SuspensionOrderAPIView, \
    PaymentOrderAPIView

urlpatterns = [
    path('employment-contract/', EmploymentContractAPIView.as_view()),
    path('suspension-order/', SuspensionOrderAPIView.as_view()),
    path('payment-order/', PaymentOrderAPIView.as_view()),
    path('notice-conclusion/', NoticeConclusionAPIView.as_view()),
]
