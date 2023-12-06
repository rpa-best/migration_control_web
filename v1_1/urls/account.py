from django.urls import include, path
# from rest_framework.routers import DefaultRouter
from v1_1.views.account import AuthView, AccountCreateAPIView, AccountDetailAPIView, MyAvatarViewSet

# router = DefaultRouter()
# router.register('avatar', MyAvatarViewSet, basename='avatars')


urlpatterns = [
    # path('', include(router.urls)),
    path('auth/', AuthView.as_view()),
    path('create/', AccountCreateAPIView.as_view()),
    # Account
    path('me/', AccountDetailAPIView.as_view()),
    path('avatar/', MyAvatarViewSet.as_view()),
]
