# from rest_framework import status
# from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveUpdateAPIView
# from rest_framework.response import Response
# from v1_1.models.user import User
# from v1_1.serializers.account import AuthSerializer, AccountCreateSerializer
# from v1_1.common_utils.token import get_token
# from django.db.transaction import atomic
# from ..swagger_content import account

from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenRefreshView
from django.db.transaction import atomic
from v1_1.common_utils.token import get_token
from v1_1.models.user import User
from v1_1.serializers.account import AccountCreateSerializer, AuthSerializer

from ..swagger_content import account


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