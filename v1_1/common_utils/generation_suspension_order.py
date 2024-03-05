from docxtpl import DocxTemplate
from django.http import HttpResponse
from v1_1.apies.DaData import GetCity
from v1_1.common_utils.functions_blanks import ConvertDate
from v1_1.models.organization import Organization, Bank, ResponsiblePersons, DirectorOrganization
from v1_1.models.worker import Worker
from v1_1.serializers.blanks import SuspensionOrderSerializer


# Приказ об отстранении
def GenerationSuspensionOrder(data):
    # =========== Входные данные, которые вводятся пользователем вручную ===========
    worker_id = data['worker_id']
    number = data['number']
    start_date = str(data['start_date'])
    reason_suspension_mapping = dict(SuspensionOrderSerializer.REASON_SUSPENSION)
    reason_suspension = reason_suspension_mapping.get(data['reason_suspension'])

    first_manager_id = data['first_manager_id']
    # ФИО 1-го менеджера по персоналу
    name_first_manager = ResponsiblePersons.objects.get(pk=first_manager_id).name
    surname_first_manager = ResponsiblePersons.objects.get(pk=first_manager_id).surname
    patronymic_first_manager = ResponsiblePersons.objects.get(pk=first_manager_id).patronymic

    # Получение инициалов 1-го менеджера по персоналу
    first_hr_manager = f'{surname_first_manager} {name_first_manager[0]}.'
    if patronymic_first_manager:
        first_hr_manager += f'{patronymic_first_manager[0]}.'

    second_manager_id = data['second_manager_id']
    # ФИО 2-го менеджера по персоналу
    name_second_manager = ResponsiblePersons.objects.get(pk=second_manager_id).name
    surname_second_manager = ResponsiblePersons.objects.get(pk=second_manager_id).surname
    patronymic_second_manager = ResponsiblePersons.objects.get(pk=second_manager_id).patronymic

    # Получение инициалов 2-го менеджера по персоналу
    second_hr_manager = f'{surname_second_manager} {name_second_manager[0]}.'
    if patronymic_second_manager:
        second_hr_manager += f'{patronymic_second_manager[0]}.'

    # ============ Данные, которые подтягиваются из базы данных ============
    organization_id = Worker.objects.get(pk=worker_id).organization_id
    # Наименование организации
    organization = Organization.objects.get(pk=organization_id)
    organizational_form = organization.get_organizational_form_display()
    organization = f'{organizational_form} {Organization.objects.get(pk=organization_id).name}'

    inn = Organization.objects.get(pk=organization_id).inn
    kpp = Organization.objects.get(pk=organization_id).kpp
    payment_account = Bank.objects.get(organization_id=organization_id).payment_account
    correspondent_account = Bank.objects.get(organization_id=organization_id).correspondent_account
    phone = Organization.objects.get(pk=organization_id).phone

    # Юридический/фактический адрес организации
    organization_address = Organization.objects.get(pk=organization_id).legal_address
    city = GetCity(organization_address)

    # ФИО директора организации
    name_director = DirectorOrganization.objects.get(organization_id=organization_id).name_director
    surname_director = DirectorOrganization.objects.get(organization_id=organization_id).surname_director
    patronymic_director = DirectorOrganization.objects.get(organization_id=organization_id).patronymic_director

    full_name_director = f'{surname_director} {name_director}'
    if patronymic_director:
        full_name_director += f' {patronymic_director}'

    # ФИО работника
    name_worker = Worker.objects.get(pk=organization_id).name
    surname_worker = Worker.objects.get(pk=organization_id).surname
    patronymic_worker = Worker.objects.get(pk=organization_id).patronymic

    full_name_worker = f'{surname_worker} {name_worker}'
    if patronymic_worker:
        full_name_worker += f' {patronymic_worker}'

    context = {
        'organization': organization,
        'number': number,
        'city': city,
        'startDateQuotes': ConvertDate(start_date, 'quotes'),
        'startDateWordMonth': ConvertDate(start_date, 'word_month'),
        'startDateStandart': ConvertDate(start_date),
        'reasonSuspension': reason_suspension,
        'firstManager': first_hr_manager,
        'secondManager': second_hr_manager,
        'inn': inn,
        'kpp': kpp,
        'phone': phone,
        'legalAddress': organization_address,
        'actualAddress': organization_address,
        'paymentAccount': payment_account,
        'correspondentAccount': correspondent_account,
        'director': full_name_director,
        'worker': full_name_worker
    }

    path_file_doc = 'v1_1/document_templates/suspension_order.docx'
    doc = DocxTemplate(path_file_doc)
    doc.render(context)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = 'attachment; filename="suspension_order.docx"'
    doc.save(response)
    return response