from docxtpl import DocxTemplate
from django.http import HttpResponse
from v1_1.apies.DaData import GetInfoBank, GetCity
from v1_1.common_utils.functions_blanks import NameDeclension, PatronymicDeclension, CountryDeclination, ConvertDate, \
    SurnameDeclension
from v1_1.models.organization import Organization, Bank, DirectorOrganization
from v1_1.models.worker import Worker, DocumentsWorker
from .custom_handler import *


# Договор возмездного оказания услуг (ГПХ)
def GenerationContractProvisionPaidServices(data):
    # =========== Входные данные, которые вводятся пользователем вручную ===========
    worker_id = data['worker_id']
    number = data['number']
    start_date = str(data['start_date'])
    start_date = ConvertDate(start_date, 'word_month')
    end_date = str(data['end_date'])
    end_date = ConvertDate(end_date, 'word_month')
    address = data['address']
    # Данные для таблицы в документе
    services = data['services']

    # ============ Данные, которые подтягиваются из базы данных ============
    organization_id = Worker.objects.get(pk=worker_id).organization_id
    # Наименование организации
    organization = Organization.objects.get(pk=organization_id)
    organizational_form = organization.get_organizational_form_display()
    organization = f'{organizational_form} {Organization.objects.get(pk=organization_id).name}'

    inn = Organization.objects.get(pk=organization_id).inn
    ogrn = Organization.objects.get(pk=organization_id).ogrn
    kpp = Organization.objects.get(pk=organization_id).kpp

    if not Bank.objects.filter(organization_id=organization_id).exists():
        raise CustomValidationError({'error': 'Нет банковских данных компании (расчетный счет, кредитный счет, '
                                              'БИК)'})

    bank = Bank.objects.get(organization_id=organization_id)
    payment_account = bank.payment_account
    correspondent_account = bank.correspondent_account
    bic = bank.bic
    name_bank = bank.name_bank

    # Юридический/фактический адрес организации
    organization_address = Organization.objects.get(pk=organization_id).legal_address
    city = GetCity(organization_address)

    if not DirectorOrganization.objects.filter(organization_id=organization_id).exists():
        raise CustomValidationError({'error': 'Нет данных о директоре компании'})

    # ФИО директора организации
    name_director = DirectorOrganization.objects.get(organization_id=organization_id).name_director
    surname_director = DirectorOrganization.objects.get(organization_id=organization_id).surname_director
    patronymic_director = DirectorOrganization.objects.get(organization_id=organization_id).patronymic_director

    # ФИО директора организации в родительном падеже
    name_director_declension = NameDeclension(name_director)
    surname_director_declension = SurnameDeclension(surname_director)
    patronymic_director_declension = PatronymicDeclension(patronymic_director)

    full_name_director = f'{surname_director} {name_director}'
    if patronymic_director:
        full_name_director += f' {patronymic_director}'

    director_declension = f'{surname_director_declension} {name_director_declension}'
    if patronymic_director_declension:
        director_declension += f' {patronymic_director_declension}'

    # ФИО работника
    worker = Worker.objects.get(pk=worker_id)
    name_worker = worker.name
    surname_worker = worker.surname
    patronymic_worker = worker.patronymic

    full_name_worker = f'{surname_worker} {name_worker}'
    if patronymic_worker:
        full_name_worker += f' {patronymic_worker}'

    # Гражданство работника
    citizenship = CountryDeclination(Worker.objects.get(pk=worker_id).citizenship).upper()

    if not DocumentsWorker.objects.filter(worker_id=worker_id, type_document='passport', archive=False).exists():
        raise CustomValidationError({'error': 'У работника нет актуального паспорта'})

    # Серия и номер паспорта работника
    passport_series = DocumentsWorker.objects.get(worker_id=worker_id, type_document='passport', archive=False).series
    passport_number = DocumentsWorker.objects.get(worker_id=worker_id, type_document='passport', archive=False).number

    # Адрес регистрации работника
    registration_address = worker.registration_address

    context = {
        'number': number,
        'startDate': start_date,
        'endDate': end_date,
        'address': address,
        'organization': organization,
        'city': city,
        'legalAddress': organization_address,
        'directorDeclension': director_declension,
        'director': full_name_director,
        'organizationINN': inn,
        'organizationKPP': kpp,
        'organizationORGN': ogrn,
        'correspondentAccount': correspondent_account,
        'paymentAccountOrganization': payment_account,
        'BIC': bic,
        'nameBank': name_bank,
        'worker': full_name_worker,
        'citizenship': citizenship,
        'passportSeries': passport_series,
        'passportNumber': passport_number,
        'registrationAddress': registration_address,
    }

    count = 0
    list_number = []
    list_name = []
    list_price = []
    for service in services:
        count += 1
        list_number.append(str(count))
        list_name.append(service['name'])
        list_price.append(str(service['price']))

    list_number = '\n\n'.join(list_number)
    list_name = '\n\n'.join(list_name)
    list_price = '\n\n'.join(list_price)

    context['count'] = list_number
    context['nameService'] = list_name
    context['price'] = list_price

    path_file_doc = 'v1_1/document_templates/contract_provision_paid_services.docx'
    doc = DocxTemplate(path_file_doc)
    doc.render(context)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = 'attachment; filename="contract_provision_paid_services.docx"'
    doc.save(response)
    return response