from django.urls import include, path
from rest_framework.routers import DefaultRouter

from v1_1.views.account import AuthView

# from v1_1.views.account import (AccountCreateAPIView, AccountDetailAPIView, AuthView, AuthWithLcResponseView,
#                                 AuthWithLcTokenView, AuthWithLcView, ChangePasswordView, MyAvatarViewSet, RefreshView,
#                                 ServiceRateCalculate, ServiceRateKeyViewset, CheckEmailView)
#
# router = DefaultRouter()
# router.register('avatars', MyAvatarViewSet, basename='avatars')
# router.register("service-rate-key", ServiceRateKeyViewset, "")

urlpatterns = [
    path('auth/', AuthView.as_view()),
    # path('create/', AccountCreateAPIView.as_view()),
    # path("check-email/", CheckEmailView.as_view()),
    # path('refresh-token/', RefreshView.as_view()),
    # # Account
    # path('me/', AccountDetailAPIView.as_view()),
    # path('change-password/', ChangePasswordView.as_view()),
    # path('guestworker/auth-url/', AuthWithLcView.as_view()),
    # path('guestworker/auth-response/', AuthWithLcResponseView.as_view()),
    # path('guestworker/auth/', AuthWithLcTokenView.as_view()),
    # # Service
    # path('service-rate-calc/', ServiceRateCalculate.as_view()),
]
