from django.urls import include, path
from v1_1.views.account import AuthView, AccountCreateAPIView

urlpatterns = [
    path('auth/', AuthView.as_view()),
    path('create/', AccountCreateAPIView.as_view()),
    # Account
    # path('me/', AccountDetailAPIView.as_view()),
]
