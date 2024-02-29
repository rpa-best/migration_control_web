from django.urls import path
from ..views.news import NewsListAPIView, NewsDetailAPIView


urlpatterns = [
    path('news/', NewsListAPIView.as_view(), name='news-list'),
    path('news/<int:pk>/', NewsDetailAPIView.as_view(), name='news-detail'),
]