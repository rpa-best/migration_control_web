from docxtpl import DocxTemplate
from datetime import datetime, timedelta
import pytz
from django.http import HttpResponse
from dateutil.relativedelta import relativedelta
from number_to_string import get_string_by_number
from v1_1.apies.DaData import GetInfoBank
from v1_1.common_utils.functions_blanks import ConvertDate
from v1_1.models.organization import Organization, Bank
from v1_1.models.worker import Worker, DocumentsWorker
from .custom_handler import *


# цены за патент в каждом регионе
dict_patent_cost = [
    {'region': 'Москва', 'price': 6600},
    {'region': 'Московская область', 'price': 6600},
    {'region': 'Санкт-Петербург', 'price': 4400},
    {'region': 'Ленинградская область', 'price': 4400},
    {'region': 'Республика Адыгея (Адыгея)', 'price': 4892},
    {'region': 'Республика Алтай', 'price': 3969},
    {'region': 'Республика Башкортостан', 'price': 4700},
    {'region': 'Республика Бурятия', 'price': 7763},
    {'region': 'Республика Дагестан', 'price': 4903},
    {'region': 'Республика Ингушетия', 'price': 4876},
    {'region': 'Кабардино-Балкарская Республика', 'price': 8172},
    {'region': 'Республика Калмыкия', 'price': 4086},
    {'region': 'Карачаево-Черкесская Республика', 'price': 5176},
    {'region': 'Республика Карелия', 'price': 8123},
    {'region': 'Республика Коми', 'price': 6320},
    {'region': 'Республика Крым', 'price': 4342},
    {'region': 'Республика Марий Эл', 'price': 5966},
    {'region': 'Республика Мордовия', 'price': 5170},
    # ==================================================
    {'region': 'Республика Саха (Якутия)', 'price': 12255},
    {'region': 'Республика Саха', 'price': 12255},
    {'region': 'Якутия', 'price': 12255},
    # ==================================================
    {'region': 'Республика Северная Осетия - Алания', 'price': 4331},
    # ==================================================
    {'region': 'Республика Татарстан (Татарстан)', 'price': 5666},
    {'region': 'Республика Татарстан', 'price': 5666},
    # ==================================================
    {'region': 'Республика Тыва', 'price': 5211},
    {'region': 'Удмуртская Республика', 'price': 5584},
    {'region': 'Республика Хакасия', 'price': 6701},
    {'region': 'Чеченская Республика', 'price': 2724},
    # ==================================================
    {'region': 'Чувашская Республика - Чувашия', 'price': 5448},
    {'region': 'Чувашская Республика', 'price': 5448},
    # ==================================================
    {'region': 'Алтайский край', 'price': 5312},
    {'region': 'Забайкальский край', 'price': 9725},
    {'region': 'Камчатский край', 'price': 7900},
    {'region': 'Краснодарский край', 'price': 6810},
    {'region': 'Красноярский край', 'price': 6701},
    {'region': 'Пермский край', 'price': 4700},
    {'region': 'Приморский край', 'price': 8717},
    {'region': 'Ставропольский край', 'price': 5993},
    {'region': 'Хабаровский край', 'price': 7355},
    {'region': 'Амурская область', 'price': 7104},
    {'region': 'Архангельская область', 'price': 4631},
    {'region': 'Астраханская область', 'price': 4974},
    {'region': 'Белгородская область', 'price': 5734},
    {'region': 'Брянская область', 'price': 5698},
    {'region': 'Владимирская область', 'price': 6350},
    {'region': 'Волгоградская область', 'price': 4903},
    {'region': 'Вологодская область', 'price': 5720},
    {'region': 'Воронежская область', 'price': 6020},
    {'region': 'Ивановская область', 'price': 4850},
    {'region': 'Иркутская область', 'price': 7984},
    {'region': 'Калининградская область', 'price': 6265},
    {'region': 'Калужская область', 'price': 6500},
    # ==================================================
    {'region': 'Кемеровская область - Кузбасс', 'price': 5857},
    {'region': 'Кемеровская область', 'price': 5857},
    {'region': 'Кузбасс', 'price': 5857},
    # ==================================================
    {'region': 'Кировская область', 'price': 5557},
    {'region': 'Костромская область', 'price': 4732},
    {'region': 'Курганская область', 'price': 5448},
    {'region': 'Курская область', 'price': 7273},
    {'region': 'Липецкая область', 'price': 5993},
    {'region': 'Магаданская область', 'price': 8172},
    {'region': 'Мурманская область', 'price': 7627},
    {'region': 'Нижегородская область', 'price': 6292},
    {'region': 'Новгородская область', 'price': 8036},
    {'region': 'Новосибирская область', 'price': 5474},
    {'region': 'Омская область', 'price': 4767},
    {'region': 'Оренбургская область', 'price': 5421},
    {'region': 'Орловская область', 'price': 5720},
    {'region': 'Пензенская область', 'price': 5312},
    {'region': 'Псковская область', 'price': 5835},
    {'region': 'Ростовская область', 'price': 4903},
    {'region': 'Рязанская область', 'price': 6674},
    {'region': 'Самарская область', 'price': 5720},
    {'region': 'Саратовская область', 'price': 5927},
    {'region': 'Сахалинская область', 'price': 7654},
    {'region': 'Свердловская область', 'price': 5950},
    {'region': 'Смоленская область', 'price': 5348},
    {'region': 'Тамбовская область', 'price': 4300},
    {'region': 'Тверская область', 'price': 8081},
    {'region': 'Томская область', 'price': 5448},
    {'region': 'Тульская область', 'price': 6280},
    {'region': 'Тюменская область', 'price': 7180},
    {'region': 'Ульяновская область', 'price': 4903},
    {'region': 'Челябинская область', 'price': 6200},
    {'region': 'Ярославская область', 'price': 5176},
    {'region': 'Севастополь', 'price': 6783},
    {'region': 'Еврейская автономная область', 'price': 6592},
    {'region': 'Ненецкий автономный округ', 'price': 6652},
    # ==================================================
    {'region': 'Ханты-Мансийский автономный округ - Югра', 'price': 6652},
    {'region': 'Ханты-Мансийский автономный округ', 'price': 6652},
    # ==================================================
    {'region': 'Чукотский автономный округ', 'price': 7900},
    {'region': 'Ямало-Ненецкий автономный округ', 'price': 10929}
]


# Функция по формированию документа платёжного поручения
def GenerationPaymentOrder(data):
    # =========== Входные данные, которые вводятся пользователем вручную ===========
    worker_id = data['worker_id']
    number_months = int(data['number_months'])

    # ============ Данные, которые подтягиваются из базы данных ============
    organization_id = Worker.objects.get(pk=worker_id).organization_id
    # Наименование организации
    organization = Organization.objects.get(pk=organization_id)
    organizational_form = organization.get_organizational_form_display()
    organization = f'{organizational_form} {Organization.objects.get(pk=organization_id).name}'

    organization_inn = Organization.objects.get(pk=organization_id).inn
    organization_kpp = Organization.objects.get(pk=organization_id).kpp

    if not Bank.objects.filter(organization_id=organization_id).exists():
        raise CustomValidationError({'error': 'Нет банковских данных компании (расчетный счет, кредитный счет, '
                                              'БИК)'})

    payment_account = Bank.objects.get(organization_id=organization_id).payment_account
    correspondent_account = Bank.objects.get(organization_id=organization_id).correspondent_account
    bic = Bank.objects.get(organization_id=organization_id).bic
    name_bank = GetInfoBank(bic)[0]['value']
    city_bank = GetInfoBank(bic)[0]['data']['payment_city']

    # ФИО работника
    name_worker = Worker.objects.get(pk=organization_id).name
    surname_worker = Worker.objects.get(pk=organization_id).surname
    patronymic_worker = Worker.objects.get(pk=organization_id).patronymic

    full_name_worker = f'{surname_worker} {name_worker}'
    if patronymic_worker:
        full_name_worker += f' {patronymic_worker}'

    if not DocumentsWorker.objects.filter(worker_id=worker_id, type_document='INN', archive=False).exists():
        raise CustomValidationError({'error': 'У работника нет ИНН'})

    # ИНН работника
    worker_inn = DocumentsWorker.objects.get(worker_id=worker_id, type_document='INN', archive=False).number
    worker_inn = 'ИНН: ' + worker_inn

    if not DocumentsWorker.objects.filter(worker_id=worker_id, type_document='patent', archive=False).exists():
        raise CustomValidationError({'error': 'У работника нет актуального патента'})

    territory_action = DocumentsWorker.objects.get(worker_id=worker_id, type_document='patent', archive=False).territory_action
    expiration_date = str(DocumentsWorker.objects.get(worker_id=worker_id, type_document='patent', archive=False).date_end)
    if expiration_date:
        expiration_date = datetime.strptime(expiration_date, '%Y-%m-%d')
    else:
        raise CustomValidationError({'error': 'Не заполнена дата окончания срока патента'})

    total_sum = 0
    # Итерация цен за патент в каждом регионе
    for obj in dict_patent_cost:
        if obj['region'] == territory_action:
            total_sum = obj['price'] * number_months
            break

    text_sum = get_string_by_number(total_sum)
    total_sum = str(total_sum)
    if len(total_sum) == 4:
        total_sum = total_sum.replace(f'{total_sum[0]}', f'{total_sum[0]} ', 1)
    elif len(total_sum) == 5:
        total_sum = total_sum.replace(f'{total_sum[0] + total_sum[1]}', f'{total_sum[0] + total_sum[1]} ', 1)
    elif len(total_sum) == 6:
        total_sum = total_sum.replace(f'{total_sum[0] + total_sum[1] + total_sum[2]}',
                                      f'{total_sum[0] + total_sum[1] + total_sum[2]} ', 1)
    total_sum = total_sum + '-00'

    renewal_date = expiration_date + relativedelta(months=number_months) - timedelta(days=1)
    renewal_date = ConvertDate(renewal_date.strftime("%d-%m-%Y"))

    expiration_date = ConvertDate(expiration_date.strftime("%d-%m-%Y"))
    period = str(expiration_date) + ' - ' + str(renewal_date)

    now_date = datetime.now(pytz.timezone('UTC'))
    now_date = now_date.strftime('%d-%m-%Y').replace('-', '.')

    context = {
        'nowDate': now_date,
        'organization': organization,
        'organizationINN': organization_inn,
        'organizationKPP': organization_kpp,
        'paymentAccount': payment_account,
        'correspondentAccount': correspondent_account,
        'BIC': bic,
        'nameBank': name_bank,
        'cityBank': city_bank,
        'fullName': full_name_worker,
        'WorkerINN': worker_inn,
        'sum': total_sum,
        'textSum': text_sum,
        'period': period,
        'individual': full_name_worker
    }

    path_file_doc = 'v1_1/document_templates/generation_payment_order.docx'
    doc = DocxTemplate(path_file_doc)
    doc.render(context)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = 'attachment; filename="generation_payment_order.docx"'
    doc.save(response)
    return response