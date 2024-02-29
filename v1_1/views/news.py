from rest_framework import generics
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from ..models.news import News
from ..serializers.news import NewsSerializer, NewsDetailSerializer


class NewsListAPIView(generics.ListAPIView):
    serializer_class = NewsSerializer
    filter_backends = [SearchFilter]
    search_fields = ['tagsnew__tag__name']

    def get_queryset(self):
        tag_name = self.request.GET.get('tag_name')  # Получаем параметр tag_name из GET запроса
        if tag_name:
            return News.objects.filter(tagsnew__tag__name=tag_name).order_by('-date_publication')
        else:
            return News.objects.all().order_by('-date_publication')


class NewsDetailAPIView(generics.RetrieveAPIView):
    queryset = News.objects.prefetch_related('tagsnew_set').all()
    serializer_class = NewsDetailSerializer