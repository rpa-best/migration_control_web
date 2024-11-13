import os
from django.utils import timezone
from rest_framework.response import Response
from django.db.models import Sum, Q, Count
from rest_framework import status, generics
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from django.db.transaction import atomic
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from v1_1.common_utils.token import get_token
from v1_1.models import User, UserPvc, HistoryPayment, OrganizationUser, Tasks
from v1_1.serializers.account import AccountCreateSerializer, AuthSerializer, AccountDetailSerializer, \
    AccountPatchSerializer, UserAvatarsSerializer, ChangePasswordSerializer, CheckEmailSerializer, \
    ValidationPasswordAndPhoneSerializer, CreatingSubscriptionSerializer, ListServiceRateSerializer, \
    CurrentRateSerializer
from ..common_utils.serializers import TokenRefreshSerializer
from ..models.subscription import ServiceRate, Subscription
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


@account.password_and_phone_validation
class ValidationPasswordAndPhoneAPIView(CreateAPIView):
    serializer_class = ValidationPasswordAndPhoneSerializer
    authentication_classes = ()
    permission_classes = ()

    def post(self, request, **kwargs):
        serializer = ValidationPasswordAndPhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Валидация прошла успешно'})


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


@account.account
class MonthlyExpensesView(RetrieveAPIView):
    permission_class = IsAuthenticated

    def get(self, request):
        """ Вывод затрат за текущий календарный месяц """

        # Получение текущей даты
        now = timezone.now()
        # Определение первый и последний день текущего месяца
        first_day_of_month = now.replace(day=1)
        last_day_of_month = (first_day_of_month + timezone.timedelta(days=31)).replace(day=1) - timezone.timedelta(days=1)

        # Фильтрация затрат пользователя за текущий месяц
        expenses = HistoryPayment.objects.filter(
            user=request.user,
            date_payment__range=(first_day_of_month, last_day_of_month)
        ).aggregate(total_amount=Sum('amount'))

        return Response({
            'total_amount': expenses['total_amount'] or 0  # Если нет затрат, возвращается 0
        })


@account.account
class ProgressTasksView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = self.request.user  # Получение авторизованного пользователя

        try:
            organization_users = OrganizationUser .objects.filter(user=user)
            # Получение списка id организаций авторизованного пользователя
            organizations = [ou.organization.id for ou in organization_users]
        except OrganizationUser .DoesNotExist:
            return Response({'error': 'Вы не связаны ни с какой организацией'}, status=400)

        # Фильтрация задач по организациям
        filter_conditions = Q(document_id__worker_id__organization_id__in=organizations)

        # Получение общего количества задач
        total_tasks = Tasks.objects.filter(filter_conditions).count()

        # Получение количества задач по статусу
        status_counts = Tasks.objects.filter(filter_conditions).values('status').annotate(count=Count('id'))

        # Создание словаря для подсчета процентов
        status_percentages = {
            'done': {'title': 'Выполнено', 'color': '#7DC066', 'count': 0},
            'overdue': {'title': 'Просрочено', 'color': '#E5646C', 'count': 0},
            'open': {'title': 'Открыто', 'color': '#59B4D1', 'count': 0},
            'shifted': {'title': 'Сдвинуто', 'color': '#F3935D', 'count': 0},
            'cancelled': {'title': 'Отменено', 'color': '#727880', 'count': 0},
        }

        # Заполнение словаря counts
        for status in status_counts:
            status_percentages[status['status']]['count'] = status['count']

        # Вычисление процентов
        if total_tasks > 0:
            for status in status_percentages.values():
                status['percentage'] = (status['count'] / total_tasks) * 100
        else:
            for status in status_percentages.values():
                status['percentage'] = 0

        # Формирование выходной структуры данных
        response_data = [
            {
                'title': status['title'],
                'percentage': status['percentage'],
                'color': status['color'],
            }
            for status in status_percentages.values()
        ]

        return Response(response_data)


@account.subscription
class CreatingSubscriptionView(CreateAPIView):
    serializer_class = CreatingSubscriptionSerializer
    permission_class = IsAuthenticated


@account.subscription
class ListServiceRateView(generics.ListAPIView):
    queryset = ServiceRate.objects.all()
    permission_classes = ()
    serializer_class = ListServiceRateSerializer


@account.subscription
class CurrentRate(RetrieveAPIView):
    queryset = Subscription.objects.all()
    serializer_class = CurrentRateSerializer

    def get_object(self):
        return self.request.user
