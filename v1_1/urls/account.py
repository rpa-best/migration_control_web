from django.urls import include, path
from v1_1.views.account import AuthView, AccountCreateAPIView, AccountDetailAPIView, MyAvatarViewSet, RefreshView, \
    ChangePasswordView, CheckEmailView, ValidationPasswordAndPhoneAPIView, CreatingSubscriptionView, \
    ListServiceRateView, CurrentRate, MonthlyExpensesView, ProgressTasksView

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
    path('monthly-expenses/', MonthlyExpensesView.as_view(), name='monthly-expenses'),
    path('progress_tasks/', ProgressTasksView.as_view(), name='progress_tasks'),
    # Подписка
    path('subscription/', CreatingSubscriptionView.as_view()),
    path('list-service-rate/', ListServiceRateView.as_view()),
    path('current-rate/', CurrentRate.as_view())
]
