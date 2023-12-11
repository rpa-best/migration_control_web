import os
from rest_framework import status, generics
from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.transaction import atomic
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from v1_1.common_utils.token import get_token
from v1_1.models.user import User
from v1_1.serializers.account import AccountCreateSerializer, AuthSerializer, AccountDetailSerializer, \
    AccountPatchSerializer, UserAvatarsSerializer
from ..common_utils.serializers import TokenRefreshSerializer
from ..swagger_content import account


@account.auth
class AuthView(CreateAPIView):
    serializer_class = AuthSerializer
    authentication_classes = ()
    permission_classes = ()


@account.create
class AccountCreateAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = AccountCreateSerializer
    authentication_classes = ()
    permission_classes = ()

    # When using the @ atomic decorator, if an exception occurs inside a block of code, all changes made to the database
    # inside that block are rolled back (i.e.undone) to keep the database in a consistent state.If no exception occurs,
    # all changes are applied and saved to the database.
    @atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        print(serializer.data)
        headers = self.get_success_headers(serializer.data)
        # Return the access token for this request and the created user object.
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


@account.account
class MyAvatarViewSet(generics.UpdateAPIView):
    permission_class = IsAuthenticated
    serializer_class = UserAvatarsSerializer

    def get_object(self):
        print(self.request.user.avatar)
        return self.request.user

    def perform_update(self, serializer):
        # getting the current avatar of the user
        current_avatar = self.request.user.avatar

        # deleting the previous avatar from the folder
        if current_avatar:
            try:
                print(current_avatar.path)
                os.remove(current_avatar.path)
            except:
                pass

        # saving a new avatar
        serializer.save()
