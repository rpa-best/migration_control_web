from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from v1_1.models.organization import OrganizationUser
from v1_1.models.subscription import Subscription
from v1_1.models.worker import Worker


class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = '__all__'

    def validate_organization(self, value):
        user = self.context['request'].user.username
        # Можно указать только ту организацию, в которой работает пользователь.
        if not OrganizationUser.objects.filter(organization=value, user_id=user).exists():
            raise ValidationError({'message': 'Вы не являетесь сотрудником этой организации'})
        else:
            return value

    def validate(self, data):
        # Получение владельца организации
        organization_owner = OrganizationUser.objects.filter(organization=data['organization'].id, role='owner').first()
        print(organization_owner)
        # Проверка на наличие активной подписки у владельца организации
        subscription = Subscription.objects.filter(user=organization_owner.user, status='active').first()
        if not subscription:
            raise ValidationError({'message': "У владельца нет активной подписки."})

        # Получение максимального количества работников, которых можно создать
        max_employees = subscription.service_rate.number_employees

        # Получение списка ИНН работников, созданных пользователем
        user_employees = Worker.objects.filter(organization__owner=organization_owner.user).values_list('inn',
                                                                                                        flat=True)
        # Подсчет количества уникальных ИНН работников
        unique_employees = len(set(user_employees))

        # Проверка на превышение лимита по количеству создаваемых работников
        if unique_employees >= max_employees:
            raise ValidationError({'message': 'Вы достигли максимального лимита на создание сотрудников.'})

        return data