from datetime import datetime
from openpyxl import *
from django.http import HttpResponse
from v1_1.common_utils.functions_blanks import CountryDeclination
from v1_1.models.organization import Organization, DirectorOrganization
from v1_1.models.worker import DocumentsWorker, Worker
from .custom_handler import *


# Уведомление о прекращении
def GenerationNoticeTermination(data):
    # =========== Входные данные, которые вводятся пользователем вручную ===========
    worker_id = data['worker_id']
    name_territorial_body = data['name_territorial_body'].upper()
    position = data['position'].upper()
    base = data['base']
    end_date = data['end_date']
    initiator = data['initiator']
    person = data['person']

    # ============ Данные, которые подтягиваются из базы данных ============
    organization_id = Worker.objects.get(pk=worker_id).organization_id
    # Наименование организации
    organization = Organization.objects.get(pk=organization_id)
    organizational_form = organization.get_organizational_form_display()
    organization = f'{organizational_form} {Organization.objects.get(pk=organization_id).name}'.upper()
    phone = Organization.objects.get(pk=organization_id).phone
    if not phone:
        raise CustomValidationError({'error': 'У компании не заполнен номер телефона'})
    inn = Organization.objects.get(pk=organization_id).inn
    kpp = Organization.objects.get(pk=organization_id).kpp
    inn_kpp = f'{inn}' + '/' + f'{kpp}'
    ogrn = f'ОГРН {Organization.objects.get(pk=organization_id).ogrn}'
    okved = Organization.objects.get(pk=organization_id).okved
    if not okved:
        raise CustomValidationError({'error': 'У компании не заполнен ОКВЭД'})
    legal_address = Organization.objects.get(pk=organization_id).legal_address.upper()

    if not DirectorOrganization.objects.filter(organization_id=organization_id).exists():
        raise CustomValidationError({'error': 'Нет данных о директоре компании'})

    # ФИО директора организации
    name_director = DirectorOrganization.objects.get(organization_id=organization_id).name_director
    surname_director = DirectorOrganization.objects.get(organization_id=organization_id).surname_director
    patronymic_director = DirectorOrganization.objects.get(organization_id=organization_id).patronymic_director

    full_name_director = f'{surname_director} {name_director}'
    if patronymic_director:
        full_name_director += f' {patronymic_director}'

    # ФИО работника
    name_worker = Worker.objects.get(pk=worker_id).name.upper()
    surname_worker = Worker.objects.get(pk=worker_id).surname.upper()
    patronymic_worker = Worker.objects.get(pk=worker_id).patronymic.upper()

    # Гражданство работника
    citizenship = CountryDeclination(Worker.objects.get(pk=worker_id).citizenship).upper()

    # Место рождения работника (в новом  бланке (2024 г) не используется
    # place_birth = CountryDeclination(Worker.objects.get(pk=worker_id).place_birth).upper()

    # Дата рождения работника
    birthday = str(Worker.objects.get(pk=worker_id).birthday).upper()
    if not birthday:
        raise CustomValidationError({'error': 'Не заполнена дата рождения сотрудника'})

    if not DocumentsWorker.objects.filter(worker_id=worker_id, type_document='passport', archive=False).exists():
        raise CustomValidationError({'error': 'У работника нет актуального паспорта'})

    # Паспортные данные работника
    passport_series = DocumentsWorker.objects.get(worker_id=worker_id, type_document='passport',
                                                  archive=False).series.upper()
    passport_number = DocumentsWorker.objects.get(worker_id=worker_id, type_document='passport',
                                                  archive=False).number.upper()
    date_issue_passport = str(
        DocumentsWorker.objects.get(worker_id=worker_id, type_document='passport', archive=False).date_issue)
    if date_issue_passport:
        date_issue_passport = datetime.strptime(date_issue_passport, '%Y-%m-%d')
        date_issue_passport = date_issue_passport.strftime('%d.%m.%Y')
    else:
        raise CustomValidationError({'error': 'Не заполнена дата выдачи паспорта'})

    issued_whom = str(
        DocumentsWorker.objects.get(worker_id=worker_id, type_document='passport', archive=False).issued_whom).upper()

    path_file_doc = 'v1_1/document_templates/termination_notice.xlsx'
    doc = load_workbook(path_file_doc)
    sheet = doc.active

    list_columns = ['A', 'C', 'E', 'G', 'I', 'K', 'M', 'O', 'Q', 'S', 'U', 'W', 'Y', 'AA', 'AC', 'AE', 'AG', 'AI',
                    'AK', 'AM', 'AO', 'AQ', 'AS', 'AU', 'AW', 'AY', 'BA', 'BC', 'BE', 'BG', 'BI', 'BK', 'BM', 'BO',
                    'BQ']

    row = 13
    index = 0
    for symbol in name_territorial_body:
        for col in range(index, len(list_columns)):
            cell = list_columns[index] + str(row)
            if list_columns[index] == 'BQ':
                sheet[f'{cell}'] = symbol
                row += 2
                index = 0
                break
            sheet[f'{cell}'] = symbol
            index += 1
            break

    list_columns_for_okved = ['AU', 'AW', 'AY', 'BA', 'BC', 'BE', 'BG', 'BI', 'BK', 'BM', 'BO', 'BQ']
    row = 38
    index = 0
    stop = False
    for symbol in okved:
        for col in range(index, len(list_columns_for_okved)):
            cell = list_columns_for_okved[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'BQ':
                stop = True
            break
        if stop == True:
            break

    row = 43
    index = 0
    for symbol in organization:
        for col in range(index, len(list_columns)):
            cell = list_columns[index] + str(row)
            if list_columns[index] == 'BQ':
                sheet[f'{cell}'] = symbol
                row += 2
                index = 0
                break
            sheet[f'{cell}'] = symbol
            index += 1
            break

    row = 60
    index = 0
    for symbol in ogrn:
        for col in range(index, len(list_columns)):
            cell = list_columns[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            break

    row = 74
    index = 0
    for symbol in inn:
        for col in range(index, len(list_columns)):
            cell = list_columns[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            break

    row = 77
    index = 0
    for symbol in legal_address:
        for col in range(index, len(list_columns)):
            cell = list_columns[index] + str(row)
            if list_columns[index] == 'BQ':
                sheet[f'{cell}'] = symbol
                row += 3
                index = 0
                break
            sheet[f'{cell}'] = symbol
            index += 1
            break

    row = 86
    index = 0
    list_columns_phone = ['U', 'W', 'Y', 'AA', 'AC', 'AE', 'AG', 'AI', 'AK', 'AM', 'AO', 'AQ', 'AS', 'AU', 'AW',
                          'AY', 'BA', 'BC', 'BE', 'BG', 'BI', 'BK', 'BM', 'BO', 'BQ']

    for symbol in phone:
        for col in range(index, len(list_columns_phone)):
            cell = list_columns_phone[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            break

    list_columns_for_full_name = ['O', 'Q', 'S', 'U', 'W', 'Y', 'AA', 'AC', 'AE', 'AG', 'AI', 'AK', 'AM', 'AO', 'AQ',
                                  'AS', 'AU', 'AW', 'AY', 'BA', 'BC', 'BE', 'BG', 'BI', 'BK', 'BM', 'BO', 'BQ']

    row = 92
    index = 0
    stop = False
    for symbol in surname_worker:
        for col in range(index, len(list_columns_for_full_name)):
            cell = list_columns_for_full_name[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'BQ':
                stop = True
            break
        if stop == True:
            break

    row = 94
    index = 0
    stop = False
    for symbol in name_worker:
        for col in range(index, len(list_columns_for_full_name)):
            cell = list_columns_for_full_name[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'BQ':
                stop = True
            break
        if stop == True:
            break

    if patronymic_worker != None and patronymic_worker != '':
        row = 96
        index = 0
        stop = False
        for symbol in patronymic_worker:
            for col in range(index, len(list_columns_for_full_name)):
                cell = list_columns_for_full_name[index] + str(row)
                sheet[f'{cell}'] = symbol
                index += 1
                if col == 'BQ':
                    stop = True
                break
            if stop == True:
                break

    list_columns_for_citizenship = ['Q', 'S', 'U', 'W', 'Y', 'AA', 'AC', 'AE', 'AG', 'AI',
                    'AK', 'AM', 'AO', 'AQ', 'AS', 'AU', 'AW', 'AY', 'BA', 'BC', 'BE', 'BG', 'BI', 'BK', 'BM', 'BO',
                    'BQ']
    row = 99
    index = 0
    stop = False
    for symbol in citizenship:
        for col in range(index, len(list_columns_for_citizenship)):
            cell = list_columns_for_citizenship[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'BQ':
                stop = True
            break
        if stop == True:
            break

    list_birthday = birthday.split('-')
    try:
        #День0
        sheet['R103'],  sheet['T103'] = list_birthday[2][0], list_birthday[2][1]
        #Месяц
        sheet['W103'], sheet['Y103'] = list_birthday[1][0], list_birthday[1][1]
        #Год
        sheet['AB103'], sheet['AD103'] = list_birthday[0][0], list_birthday[0][1]
        sheet['AF103'], sheet['AH103'] = list_birthday[0][2], list_birthday[0][3]
    except:
        raise CustomValidationError({'error': 'У сотрудника не указана дата рождения'})

    # ============= Запись паспорта =============
    list_columns_for_passport_series = ['G', 'I', 'K', 'M', 'O', 'Q', 'S']
    row = 109
    index = 0
    stop = False
    for symbol in passport_series:
        for col in range(index, len(list_columns_for_passport_series)):
            cell = list_columns_for_passport_series[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'S':
                stop = True
            break
        if stop == True:
            break

    list_columns_for_passport_number = ['Z', 'AB', 'AD', 'AF', 'AH', 'AJ', 'AL', 'AN', 'AP']
    row = 109
    index = 0
    stop = False
    for symbol in passport_number:
        for col in range(index, len(list_columns_for_passport_number)):
            cell = list_columns_for_passport_number[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'AP':
                stop = True
            break
        if stop == True:
            break

    list_date_issue_passport = date_issue_passport.split('.')
    #День
    sheet['BA109'],  sheet['BC109'] = list_date_issue_passport[0][0], list_date_issue_passport[0][1]
    #Месяц
    sheet['BF109'], sheet['BH109'] = list_date_issue_passport[1][0], list_date_issue_passport[1][1]
    #Год
    sheet['BK109'], sheet['BM109'] = list_date_issue_passport[2][0], list_date_issue_passport[2][1]
    sheet['BO109'], sheet['BQ109'] = list_date_issue_passport[2][2], list_date_issue_passport[2][3]

    list_columns_for_publisher = ['O', 'Q', 'S', 'U', 'W', 'Y', 'AA', 'AC', 'AE', 'AG', 'AI', 'AK', 'AM', 'AO', 'AQ',
                                  'AS', 'AU', 'AW', 'AY', 'BA', 'BC', 'BE', 'BG', 'BI', 'BK', 'BM', 'BO', 'BQ']
    list_columns_for_publisher_last = ['AD', 'AF', 'AH', 'AJ', 'AL', 'AN', 'AP', 'AR', 'AT', 'AV', 'AX', 'AZ', 'BB']
    row = 112
    index_publisher_last = 0
    stop = False
    for symbol in issued_whom:
        if row == 117:
            for col in range(index_publisher_last, len(list_columns_for_publisher_last)):
                cell = list_columns_for_publisher_last[index_publisher_last] + str(row)
                sheet[f'{cell}'] = symbol
                index_publisher_last += 1
                if col == 'BB':
                    stop = True
                break
            if stop == True:
                break
        else:
            for col in range(index, len(list_columns_for_publisher)):
                cell = list_columns_for_publisher[index] + str(row)
                if list_columns_for_publisher[index] == 'BQ':
                    sheet[f'{cell}'] = symbol
                    row += 2
                    index = 0
                    break
                sheet[f'{cell}'] = symbol
                index += 1
                break
    # =======================================================================

    # ============= Запись патента =============
    if DocumentsWorker.objects.filter(worker_id=worker_id, type_document='patent', archive=False).exists():
        # Данные патента работника
        series_patent = DocumentsWorker.objects.get(worker_id=worker_id, type_document='patent',
                                                    archive=False).series.upper()
        number_patent = DocumentsWorker.objects.get(worker_id=worker_id, type_document='patent',
                                                    archive=False).number.upper()
        date_issue_patent = str(
            DocumentsWorker.objects.get(worker_id=worker_id, type_document='patent', archive=False).date_issue)
        issued_whom = DocumentsWorker.objects.get(worker_id=worker_id, type_document='patent',
                                                  archive=False).issued_whom.upper()
        date_end_patent = str(
            DocumentsWorker.objects.get(worker_id=worker_id, type_document='patent', archive=False).date_end)

        list_columns_for_patent_series = ['G', 'I', 'K', 'M', 'O', 'Q', 'S']
        row = 124
        index = 0
        stop = False
        for symbol in series_patent:
            for col in range(index, len(list_columns_for_patent_series)):
                cell = list_columns_for_patent_series[index] + str(row)
                sheet[f'{cell}'] = symbol
                index += 1
                if col == 'S':
                    stop = True
                break
            if stop == True:
                break

        list_columns_for_patent_number = ['X', 'Z', 'AB', 'AD', 'AF', 'AH', 'AJ', 'AL', 'AN', 'AP']
        row = 124
        index = 0
        stop = False
        for symbol in number_patent:
            for col in range(index, len(list_columns_for_patent_number)):
                cell = list_columns_for_patent_number[index] + str(row)
                sheet[f'{cell}'] = symbol
                index += 1
                if col == 'AP':
                    stop = True
                break
            if stop == True:
                break

        list_date_issue_patent = date_issue_patent.split('-')
        # День
        sheet['BA124'], sheet['BC124'] = list_date_issue_patent[2][0], list_date_issue_patent[2][1]
        # Месяц
        sheet['BF124'], sheet['BH124'] = list_date_issue_patent[1][0], list_date_issue_patent[1][1]
        # Год
        sheet['BK124'], sheet['BM124'] = list_date_issue_patent[0][0], list_date_issue_patent[0][1]
        sheet['BO124'], sheet['BQ124'] = list_date_issue_patent[0][2], list_date_issue_patent[0][3]

        list_columns_for_publisher = ['Q', 'S', 'U', 'W', 'Y', 'AA', 'AC', 'AE', 'AG', 'AI', 'AK', 'AM', 'AO', 'AQ',
                                      'AS', 'AU', 'AW', 'AY', 'BA', 'BC', 'BE', 'BG', 'BI', 'BK', 'BM', 'BO', 'BQ']
        list_columns_for_publisher_last = ['A', 'C', 'E', 'G', 'I', 'K', 'M', 'O', 'Q', 'S', 'U', 'W', 'Y', 'AA', 'AC',
                                           'AE', 'AG', 'AI', 'AK', 'AM', 'AO', 'AQ', 'AS', 'AU', 'AW', 'AY', 'BA', 'BC',
                                           'BE', 'BG', 'BI', 'BK', 'BM', 'BO', 'BQ']
        row = 126
        index_publisher_last = 0
        stop = False
        for symbol in issued_whom:
            if row == 128:
                for col in range(index_publisher_last, len(list_columns_for_publisher_last)):
                    cell = list_columns_for_publisher_last[index_publisher_last] + str(row)
                    sheet[f'{cell}'] = symbol
                    index_publisher_last += 1
                    if col == 'BQ':
                        stop = True
                    break
                if stop == True:
                    break
            else:
                for col in range(index, len(list_columns_for_publisher)):
                    cell = list_columns_for_publisher[index] + str(row)
                    if list_columns_for_publisher[index] == 'BQ':
                        sheet[f'{cell}'] = symbol
                        row += 2
                        index = 0
                        break
                    sheet[f'{cell}'] = symbol
                    index += 1
                    break

        # День
        sheet['P130'], sheet['R130'] = list_date_issue_patent[2][0], list_date_issue_patent[2][1]
        # Месяц
        sheet['U130'], sheet['W130'] = list_date_issue_patent[1][0], list_date_issue_patent[1][1]
        # Год
        sheet['Z130'], sheet['AB130'] = list_date_issue_patent[0][0], list_date_issue_patent[0][1]
        sheet['AD130'], sheet['AF130'] = list_date_issue_patent[0][2], list_date_issue_patent[0][3]

        date_end_patent = date_end_patent.split('-')
        # День
        sheet['AL130'], sheet['AN130'] = date_end_patent[2][0], date_end_patent[2][1]
        # Месяц
        sheet['AQ130'], sheet['AS130'] = date_end_patent[1][0], date_end_patent[1][1]
        # Город
        sheet['AV130'], sheet['AX130'] = date_end_patent[0][0], date_end_patent[0][1]
        sheet['AZ130'], sheet['BB130'] = date_end_patent[0][2], date_end_patent[0][3]
    # ===========================================
    else:
        if (citizenship == 'Киргизия' or citizenship == 'Армения' or citizenship == 'Казахстан' or
                citizenship == 'Беларусь' or citizenship == 'Республика Беларусь'):
            name_international_agreement = "П. 1, СТАТЬИ 97, ДОГОВОРА О ЕВРАЗИЙСКОМ ЭКОНОМИЧЕСКОМ СОЮЗЕ ОТ 29.05.2014 (В РЕД. ОТ 08.05.2015)"
            row = 145
            index = 0
            for symbol in name_international_agreement:
                for col in range(index, len(list_columns)):
                    cell = list_columns[index] + str(row)
                    if list_columns[index] == 'BQ':
                        sheet[f'{cell}'] = symbol
                        row += 2
                        index = 0
                        break
                    sheet[f'{cell}'] = symbol
                    index += 1
                    break

    row = 150
    index = 0
    for symbol in position:
        for col in range(index, len(list_columns)):
            cell = list_columns[index] + str(row)
            if list_columns[index] == 'BQ':
                sheet[f'{cell}'] = symbol
                row += 2
                index = 0
                break
            sheet[f'{cell}'] = symbol
            index += 1
            break

    if 'employment_contract' in base:
        sheet['A160'] = 'X'
    else:
        sheet['W160'] = 'X'

    arr_date = end_date.split('-')[::-1]
    # День
    sheet['AX166'] = arr_date[0][0]
    sheet['AZ166'] = arr_date[0][1]
    # Месяц
    sheet['BC166'] = arr_date[1][0]
    sheet['BE166'] = arr_date[1][1]
    # Год
    sheet['BH166'] = arr_date[2][0]
    sheet['BJ166'] = arr_date[2][1]
    sheet['BL166'] = arr_date[2][2]
    sheet['BN166'] = arr_date[2][3]

    if initiator:
        sheet['E173'] = 'X'
    else:
        sheet['M173'] = 'X'

    sheet['AK182'] = full_name_director

    if person == 'person_proxy':
        try:
            full_name = data['full_name']
            passport_series = data['series']
            passport_number = data['number']
            date_issue = data['date_issue']
            issued_by = data['issued_by']

            sheet['AE192'] = full_name

            if len(passport_series) == 4:
                passport_series = passport_series[0] + passport_series[1] + ' ' + passport_series[2] + passport_series[3]
            sheet['G194'] = passport_series
            sheet['X194'] = passport_number
            date_issue = '.'.join(str(date_issue).split('-')[::-1])
            sheet['AR194'] = date_issue
            sheet['J196'] = issued_by
        except:
            pass

    else:
        if not DirectorOrganization.objects.filter(organization_id=organization_id).exists():
            raise CustomValidationError({'error': 'Нет данных о директоре компании'})

        sheet["AE192"] = full_name_director
        passport_series = DirectorOrganization.objects.get(organization_id=organization_id).passport_series
        passport_number = DirectorOrganization.objects.get(organization_id=organization_id).passport_number
        if not passport_series and not passport_number:
            raise CustomValidationError({'error': 'Не заполнена серия и номер паспорта у директора компании'})
        date_issue = DirectorOrganization.objects.get(organization_id=organization_id).date_issue_passport
        if not date_issue:
            raise CustomValidationError({'error': 'Не заполнена дата выдачи паспорта у директора компании'})
        issued_whom = DirectorOrganization.objects.get(organization_id=organization_id).issued_whom
        if not issued_whom:
            raise CustomValidationError({'error': 'Не заполнен орган выдачи паспорта у директора компании'})

        if len(passport_series) == 4:
            passport_series = passport_series[0] + passport_series[1] + ' ' + passport_series[2] + passport_series[3]
        sheet["G194"] = passport_series
        sheet["X194"] = passport_number
        date_issue = '.'.join(str(date_issue).split('-')[::-1])
        sheet["AR194"] = date_issue
        sheet["J196"] = issued_whom

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="notice_termination.xlsx"'
    doc.save(response)
    return response
