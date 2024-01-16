import os
from django.middleware import csrf
from rest_framework import status, generics
from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.transaction import atomic
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from migration_control_web import settings
from v1_1.common_utils.token import get_token, RefreshToken
from v1_1.models.user import User, UserPvc
from v1_1.serializers.account import AccountCreateSerializer, AuthSerializer, AccountDetailSerializer, \
    AccountPatchSerializer, UserAvatarsSerializer, ChangePasswordSerializer, CheckEmailSerializer
from ..common_utils.serializers import TokenRefreshSerializer
from ..swagger_content import account


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

@account.auth
class AuthView(CreateAPIView):
    serializer_class = AuthSerializer
    authentication_classes = ()
    permission_classes = ()

    # def post(self, request, *args, **kwargs):
    #     response = super().post(request, *args, **kwargs)
    #     refresh_token = response.data['refresh']
    #     access_token = response.data['access']
    #
    #     response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)  # Установка куки с Refresh токеном
    #     response.data['refresh'] = 'refresh_token'  # Заменяет Refresh токен на имя куки
    #
    #     response.data['access'] = 'access_token'  # Заменяет Access токен на имя куки
    #
    #     return response

    # def post(self, request, *args, **kwargs):
    #     data = request.data
    #     response = Response()
    #     username = data.get('username', None)
    #     password = data.get('password', None)
    #     print(username)
    #     user = User.objects.get(username=username, password=password)
    #
    #     if user is not None:
    #         if user.is_active:
    #             data = get_tokens_for_user(user)
    #             response.set_cookie(
    #                 key=settings.SIMPLE_JWT['AUTH_COOKIE'],
    #                 value=data["access"],
    #                 expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
    #                 secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
    #                 httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
    #                 samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
    #             )
    #             csrf.get_token(request)
    #             response.data = data
    #             return response
    #         else:
    #             return Response({"No active": "This account is not active!!"}, status=status.HTTP_404_NOT_FOUND)
    #     else:
    #         return Response({"Invalid": "Invalid username or password!!"}, status=status.HTTP_404_NOT_FOUND)


@account.create
class AccountCreateAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = AccountCreateSerializer
    authentication_classes = ()
    permission_classes = ()

    # При использовании декоратора @atomic, если внутри блока кода возникает исключение, все изменения, внесенные
    # в базу данных внутри этого блока, откатываются (т.е. отменяются), чтобы сохранить базу данных в согласованном
    # состоянии. Если исключение не возникает, все изменения применяются и сохраняются в базе данных
    @atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # Возвращает токен доступа для этого запроса и созданный пользовательский объект.
        token = get_token(request, serializer.instance)
        return Response({
            'access': str(token.access_token),
            'refresh': str(token),
            'user': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)


@account.refresh
class RefreshView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer
    permission_classes = ()
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context=self.get_serializer_context())

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


@account.account
class AccountDetailAPIView(RetrieveUpdateAPIView):
    queryset = User.objects.all()
    permission_class = IsAuthenticated

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            serializer_class = AccountPatchSerializer
        else:
            serializer_class = AccountDetailSerializer
        return serializer_class

    def get_object(self):
        return self.request.user


@account.change_password
class ChangePasswordView(CreateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = ()
    authentication_classes = ()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)


@account.email_check
class CheckEmailView(CreateAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = CheckEmailSerializer

    def create(self, request, *args, **kwargs):
        # Получение значения email из запроса
        email = request.data.get('email')
        # Поиск последнего экземпляра UserPvc с указанным email
        instance = UserPvc.objects.filter(email=email).last()
        # Создание сериализатора на основе данных из запроса, если экземпляр не найден,
        # или на основе найденного экземпляра, если он есть
        serializer = self.get_serializer(data=request.data) if not instance else self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # Возвращение ответа с сообщением об успешной отправке кода
        return Response({'message': 'PVC sended'})


@account.account
class MyAvatarViewSet(generics.UpdateAPIView):
    permission_class = IsAuthenticated
    serializer_class = UserAvatarsSerializer

    def get_object(self):
        print(self.request.user.avatar)
        return self.request.user

    def perform_update(self, serializer):
        # получение текущего аватара пользователя
        current_avatar = self.request.user.avatar

        # удаление предыдущего аватара из папки
        if current_avatar:
            try:
                os.remove(current_avatar.path)
            except:
                pass

        # сохранение нового аватара
        serializer.save()
