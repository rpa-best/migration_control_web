from django.urls import path
from v1_1.views.blanks import NoticeConclusionAPIView

urlpatterns = [
    path('notice-conclusion/', NoticeConclusionAPIView.as_view()),
]
