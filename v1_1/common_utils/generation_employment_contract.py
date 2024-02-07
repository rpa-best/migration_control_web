from datetime import datetime
from docxtpl import DocxTemplate
from number_to_string import get_string_by_number
from django.http import HttpResponse
from v1_1.apies.DaData import GetCity, GetInfoBank
from v1_1.common_utils.functions_blanks import ConvertDate, CountryDeclination, PatronymicDeclension, SurnameDeclension, \
    NameDeclension
from v1_1.models.organization import Organization, Bank
from v1_1.models.worker import Worker, DocumentsWorker


def GenerationEmploymentContractDocument(data):
    # =========== Входные данные, которые вводятся пользователем вручную ===========
    worker_id = data['worker_id']
    contract_type = data['contract_type']
    cause = data['cause']
    number = data['number']
    position = data['position']
    salary = data['salary']
    text_salary = get_string_by_number(data['salary']).replace(' рублей 00 копеек', '', 1)

    start_time = str(data['start_time'])
    if start_time[0] == '0':
        start_time = start_time[1:]
    end_time = str(data['end_time'])
    if end_time[0] == '0':
        end_time = end_time[1:]

    start_date = data['start_date']

    start_date_word_month = ConvertDate(start_date, 'word_month')
    if contract_type == 'perpetual':
        date_content = f' и является бессрочным Дата начала работы по настоящему Договору: {start_date_word_month}'
    else:
        end_date_word_month = ConvertDate(data['end_date_urgent'], 'word_month')
        cause = data['cause']
        date_content = (f'. Настоящий трудовой договор является срочным, заключается на срок с {start_date_word_month} '
                        f'по {end_date_word_month} Обстоятельства (причины), послужившие основанием для заключения '
                        f'срочного трудового договора, - {cause}')

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
    bic = Bank.objects.get(organization_id=organization_id).bic
    name_bank = GetInfoBank(bic)[0]['value']
    phone = Organization.objects.get(pk=organization_id).phone

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

    full_name_declension = f'{surname_director_declension} {name_director_declension}'
    if patronymic_director_declension:
        full_name_declension += f' {patronymic_director_declension}'

    full_name_director = f'{surname_director} {name_director}'
    if patronymic_director:
        full_name_director += f' {patronymic_director}'

    # Получение инициалов директора
    surname_initials_director = f'{surname_director_declension} {name_director[0]}.'
    if patronymic_director:
        surname_initials_director += f'{patronymic_director[0]}.'

    # Гражданство работника
    citizenship = CountryDeclination(Worker.objects.get(pk=worker_id).citizenship).upper()

    # ФИО работника
    name_worker = Worker.objects.get(pk=organization_id).name
    surname_worker = Worker.objects.get(pk=organization_id).surname
    patronymic_worker = Worker.objects.get(pk=organization_id).patronymic

    full_name_worker = f'{surname_worker} {name_worker}'
    if patronymic_worker:
        full_name_worker += f' {patronymic_worker}'

    birthday = str(Worker.objects.get(pk=organization_id).birthday)
    birthday = birthday.split('-')
    birthday = birthday[2] + '.' + birthday[1] + '.' + birthday[0]

    passport_series = DocumentsWorker.objects.get(worker_id=worker_id, type_document='passport', archive=False).series
    passport_number = DocumentsWorker.objects.get(worker_id=worker_id, type_document='passport', archive=False).number
    passport = f'{passport_series} {passport_number}' if passport_series != '' else passport_number
    date_issue_passport = str(DocumentsWorker.objects.get(worker_id=worker_id, type_document='passport', archive=False).date_issue)
    date_issue_passport = datetime.strptime(date_issue_passport, '%Y-%m-%d')
    date_issue_passport = date_issue_passport.strftime('%d.%m.%Y')

    patent_series = DocumentsWorker.objects.get(worker_id=worker_id, type_document='patent', archive=False).series
    patent_number = DocumentsWorker.objects.get(worker_id=worker_id, type_document='patent', archive=False).number
    patent = f'{patent_series} {patent_number}'
    date_issue_patent = str(DocumentsWorker.objects.get(worker_id=worker_id, type_document='patent', archive=False).date_issue)
    date_issue_patent = datetime.strptime(date_issue_patent, '%Y-%m-%d')
    date_issue_patent = date_issue_patent.strftime('%d.%m.%Y')
    date_end_patent = str(DocumentsWorker.objects.get(worker_id=worker_id, type_document='patent', archive=False).date_end)
    date_end_patent = datetime.strptime(date_end_patent, '%Y-%m-%d')
    date_end_patent = date_end_patent.strftime('%d.%m.%Y')

    context = {
        'organization': organization,
        'director': full_name_director,
        'number': number,
        'position': position,
        'salary': salary,
        'textSalary': text_salary,
        'startDateQuotes': ConvertDate(start_date, 'quotes'),
        'startDateWordMonth': ConvertDate(start_date, 'word_month'),
        'startDateStandart': ConvertDate(start_date),
        'dateContent': date_content,
        'startTime': start_time,
        'endTime': end_time,
        'inn': inn,
        'kpp': kpp,
        'phone': phone,
        'city': city,
        'legalAddress': organization_address,
        'actualAddress': organization_address,
        'paymentAccount': payment_account,
        'correspondentAccount': correspondent_account,
        'surnameInitialsDirector': surname_initials_director,
        'fullNameDirector': full_name_director,
        'fullName': full_name_worker,
        'citizenship': citizenship,
        'birthDay': birthday,
        'BIC': bic,
        'nameBank': name_bank,
        'dateIssuePassport': date_issue_passport,
        'dateIssuePatent': date_issue_patent,
        'endDatePassport': date_end_patent,
        'passport': passport,
        'patent': patent
    }

    path_file_doc = 'v1_1/document_templates/employment_contract.docx'
    doc = DocxTemplate(path_file_doc)
    doc.render(context)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = 'attachment; filename="employment_contract.docx"'
    doc.save(response)
    return response