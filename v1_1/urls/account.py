from django.urls import include, path
from v1_1.views.account import AuthView, AccountCreateAPIView, AccountDetailAPIView, MyAvatarViewSet, RefreshView, \
    ChangePasswordView, CheckEmailView, ValidationPasswordAndPhoneAPIView, CreatingSubscriptionView

urlpatterns = [
    path('auth/', AuthView.as_view()),
    path('create/', AccountCreateAPIView.as_view()),
    path('password-and-phone-validation/', ValidationPasswordAndPhoneAPIView.as_view()),
    path('check-email/', CheckEmailView.as_view()),
    path('refresh-token/', RefreshView.as_view()),
    # Профиль пользователя
    path('me/', AccountDetailAPIView.as_view()),
    path('change-password/', ChangePasswordView.as_view()),
    path('avatar/', MyAvatarViewSet.as_view()),
    # Подписка
    path('subscription/', CreatingSubscriptionView.as_view())

]
