from docxtpl import DocxTemplate
from django.http import HttpResponse
from v1_1.apies.DaData import GetInfoBank, GetCity
from v1_1.common_utils.functions_blanks import NameDeclension, PatronymicDeclension, CountryDeclination, ConvertDate, \
    SurnameDeclension
from v1_1.models.organization import Organization, Bank
from v1_1.models.worker import Worker, DocumentsWorker


def GenerationContractProvisionPaidServices(data):
    worker_id = data['worker_id']
    number = data['number']
    start_date = str(data['start_date'])
    start_date = ConvertDate(start_date, 'word_month')
    end_date = str(data['end_date'])
    end_date = ConvertDate(end_date, 'word_month')
    address = data['address']

    # data table
    name_service = data['name_service']
    price = data['price']

    # ============ Данные, которые подтягиваются из базы данных ============
    organization_id = Worker.objects.get(pk=worker_id).organization_id
    # Наименование организации
    organization = Organization.objects.get(pk=organization_id)
    organizational_form = organization.get_organizational_form_display()
    organization = f'{organizational_form} {Organization.objects.get(pk=organization_id).name}'

    inn = Organization.objects.get(pk=organization_id).inn
    ogrn = Organization.objects.get(pk=organization_id).ogrn
    kpp = Organization.objects.get(pk=organization_id).kpp
    payment_account = Bank.objects.get(organization_id=organization_id).payment_account
    correspondent_account = Bank.objects.get(organization_id=organization_id).correspondent_account
    bic = Bank.objects.get(organization_id=organization_id).bic
    name_bank = GetInfoBank(bic)[0]['value']

    # Юридический/фактический адрес организации
    organization_address = Organization.objects.get(pk=organization_id).legal_address
    city = GetCity(organization_address)

    # ФИО директора организации
    name_director = Organization.objects.get(pk=organization_id).name_director
    surname_director = Organization.objects.get(pk=organization_id).surname_director
    patronymic_director = Organization.objects.get(pk=organization_id).patronymic_director

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
    name_worker = Worker.objects.get(pk=organization_id).name
    surname_worker = Worker.objects.get(pk=organization_id).surname
    patronymic_worker = Worker.objects.get(pk=organization_id).patronymic

    full_name_worker = f'{surname_worker} {name_worker}'
    if patronymic_worker:
        full_name_worker += f' {patronymic_worker}'

    # Гражданство работника
    citizenship = CountryDeclination(Worker.objects.get(pk=worker_id).citizenship).upper()

    # Серия и номер паспорта работника
    passport_series = DocumentsWorker.objects.get(worker_id=worker_id, type_document='passport', archive=False).series
    passport_number = DocumentsWorker.objects.get(worker_id=worker_id, type_document='passport', archive=False).number

    # Адрес регистрации работника
    registration_address = Worker.objects.get(pk=organization_id).registration_address

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
        'nameService': name_service,
        'price': price,
    }

    path_file_doc = 'v1_1/document_templates/contract_provision_paid_services.docx'
    doc = DocxTemplate(path_file_doc)
    doc.render(context)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = 'attachment; filename="contract_provision_paid_services.docx"'
    doc.save(response)
    return response