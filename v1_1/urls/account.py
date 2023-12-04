from django.urls import include, path
from v1_1.views.account import AuthView


urlpatterns = [
    path('auth/', AuthView.as_view()),
]
