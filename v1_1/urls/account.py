from django.urls import include, path
from v1_1.views.account import AuthView, AccountCreateAPIView, AccountDetailAPIView, MyAvatarViewSet, RefreshView, \
    ChangePasswordView


urlpatterns = [
    path('auth/', AuthView.as_view()),
    path('create/', AccountCreateAPIView.as_view()),
    path('refresh-token/', RefreshView.as_view()),
    # Account
    path('me/', AccountDetailAPIView.as_view()),
    path('change-password/', ChangePasswordView.as_view()),
    path('avatar/', MyAvatarViewSet.as_view()),
]
