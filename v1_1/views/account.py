from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveUpdateAPIView
from v1_1.models.user import User
from v1_1.serializers.account import AuthSerializer
# from ..swagger_content import account


# @account.auth
class AuthView(CreateAPIView):
    serializer_class = AuthSerializer
    authentication_classes = ()
    permission_classes = ()


# @account.create
# class AccountCreateAPIView(CreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = AccountCreateSerializer
#     authentication_classes = ()
#     permission_classes = ()