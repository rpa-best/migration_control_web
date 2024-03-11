from datetime import datetime
from openpyxl import *
from django.http import HttpResponse
from v1_1.common_utils.functions_blanks import CountryDeclination
from v1_1.models.organization import Organization, DirectorOrganization
from v1_1.models.worker import DocumentsWorker, Worker
from .custom_handler import *


# Уведомление о заключении
def GenerationNoticeConclusion(data):
    # =========== Входные данные, которые вводятся пользователем вручную ===========
    worker_id = data['worker_id']
    name_territorial_body = data['name_territorial_body'].upper()
    position = data['position'].upper()
    base = data['base']
    start_date = data['start_date']
    address = data['address'].upper()
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
    passport_series = DocumentsWorker.objects.get(worker_id=worker_id, type_document='passport', archive=False).series.upper()
    passport_number = DocumentsWorker.objects.get(worker_id=worker_id, type_document='passport', archive=False).number.upper()
    date_issue_passport = str(DocumentsWorker.objects.get(worker_id=worker_id, type_document='passport', archive=False).date_issue)
    if date_issue_passport:
        date_issue_passport = datetime.strptime(date_issue_passport, '%Y-%m-%d')
        date_issue_passport = date_issue_passport.strftime('%d.%m.%Y')
    else:
        raise CustomValidationError({'error': 'Не заполнена дата выдачи паспорта'})

    issued_whom = str(DocumentsWorker.objects.get(worker_id=worker_id, type_document='passport', archive=False).issued_whom).upper()

    path_file_doc = 'v1_1/document_templates/notice_conclusion.xlsx'
    doc = load_workbook(path_file_doc)
    sheet = doc.active

    list_columns = ['A', 'C', 'E', 'G', 'I', 'K', 'M', 'O', 'Q', 'S', 'U', 'W', 'Y', 'AA', 'AC', 'AE', 'AG', 'AI', 'AK',
                    'AM', 'AO', 'AQ', 'AS', 'AU', 'AW', 'AY', 'BA', 'BC', 'BE', 'BG', 'BI', 'BK', 'BM', 'BO', 'BQ']

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

    row = 75
    index = 0
    for symbol in inn:
        for col in range(index, len(list_columns)):
            cell = list_columns[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            break

    row = 78
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

    row = 87
    index = 0
    list_columns_phone = ['U', 'W', 'Y', 'AA', 'AC', 'AE', 'AG', 'AI', 'AK', 'AM', 'AO', 'AQ', 'AS', 'AU', 'AW', 'AY',
                          'BA', 'BC', 'BE', 'BG', 'BI', 'BK', 'BM', 'BO', 'BQ']
    for symbol in phone:
        for col in range(index, len(list_columns_phone)):
            cell = list_columns_phone[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            break

    list_columns_for_full_name = ['O', 'Q', 'S', 'U', 'W', 'Y', 'AA', 'AC', 'AE', 'AG', 'AI', 'AK', 'AM', 'AO', 'AQ',
                                  'AS', 'AU', 'AW', 'AY', 'BA', 'BC', 'BE', 'BG', 'BI', 'BK', 'BM', 'BO', 'BQ']

    row = 93
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

    row = 95
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
        row = 97
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

    list_columns_for_citizenship = ['Q', 'S', 'U', 'W', 'Y', 'AA', 'AC', 'AE', 'AG', 'AI', 'AK', 'AM', 'AO', 'AQ',
                                    'AS', 'AU', 'AW', 'AY', 'BA', 'BC', 'BE', 'BG', 'BI', 'BK', 'BM', 'BO', 'BQ']
    row = 100
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

    # list_columns_for_citizenship = ['W', 'Y', 'AA', 'AC', 'AE', 'AG', 'AI', 'AK', 'AM', 'AO', 'AQ', 'AS', 'AU', 'AW',
    #                                 'AY', 'BA', 'BC', 'BE', 'BG', 'BI', 'BK', 'BM', 'BO', 'BQ']
    # row = 100
    # index = 0
    # index_citizenship_last = 0
    # stop = False
    # for symbol in place_birth:
    #     if row == 103:
    #         for col in range(index_citizenship_last, len(list_columns)):
    #             cell = list_columns[index_citizenship_last] + str(row)
    #             sheet[f'{cell}'] = symbol
    #             index_citizenship_last += 1
    #             if col == 'BQ':
    #                 stop = True
    #             break
    #         if stop == True:
    #             break
    #     else:
    #         for col in range(index, len(list_columns_for_citizenship)):
    #             cell = list_columns_for_citizenship[index] + str(row)
    #             if list_columns_for_citizenship[index] == 'BQ':
    #                 sheet[f'{cell}'] = symbol
    #                 row += 3
    #                 index = 0
    #                 break
    #             sheet[f'{cell}'] = symbol
    #             index += 1
    #             break

    list_birthday = birthday.split('-')
    print(list_birthday)
    #День
    sheet['R104'],  sheet['T104'] = list_birthday[2][0], list_birthday[2][1]
    #Месяц
    sheet['W104'], sheet['Y104'] = list_birthday[1][0], list_birthday[1][1]
    #Год
    sheet['AB104'], sheet['AD104'] = list_birthday[0][0], list_birthday[0][1]
    sheet['AF104'], sheet['AH104'] = list_birthday[0][2], list_birthday[0][3]

    list_columns_for_passport_series = ['G', 'I', 'K', 'M', 'O', 'Q', 'S']
    row = 110
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
    row = 110
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
    sheet['BA110'],  sheet['BC110'] = list_date_issue_passport[0][0], list_date_issue_passport[0][1]
    #Месяц
    sheet['BF110'], sheet['BH110'] = list_date_issue_passport[1][0], list_date_issue_passport[1][1]
    #Год
    sheet['BK110'], sheet['BM110'] = list_date_issue_passport[2][0], list_date_issue_passport[2][1]
    sheet['BO110'], sheet['BQ110'] = list_date_issue_passport[2][2], list_date_issue_passport[2][3]

    list_columns_for_issued_whom = ['O', 'Q', 'S', 'U', 'W', 'Y', 'AA', 'AC', 'AE', 'AG', 'AI', 'AK', 'AM', 'AO',
                                    'AQ', 'AS', 'AU', 'AW', 'AY', 'BA', 'BC', 'BE', 'BG', 'BI', 'BK', 'BM', 'BO', 'BQ']
    list_columns_for_list_columns_for_issued_whom_last = ['AD', 'AF', 'AH', 'AJ', 'AL', 'AN', 'AP', 'AR', 'AT', 'AV',
                                                          'AX', 'AZ', 'BB']
    row = 113
    index = 0
    index_publisher_last = 0
    stop = False
    for symbol in issued_whom:
        if row == 118:
            for col in range(index_publisher_last, len(list_columns_for_list_columns_for_issued_whom_last)):
                cell = list_columns_for_list_columns_for_issued_whom_last[index_publisher_last] + str(row)
                sheet[f'{cell}'] = symbol
                index_publisher_last += 1
                if col == 'BB':
                    stop = True
                break
            if stop == True:
                break
        else:
            for col in range(index, len(list_columns_for_issued_whom)):
                cell = list_columns_for_issued_whom[index] + str(row)
                if list_columns_for_issued_whom[index] == 'BQ':
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
        row = 130
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
        row = 130
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
        sheet['BA130'], sheet['BC130'] = list_date_issue_patent[2][0], list_date_issue_patent[2][1]
        # Месяц
        sheet['BF130'], sheet['BH130'] = list_date_issue_patent[1][0], list_date_issue_patent[1][1]
        # Год
        sheet['BK130'], sheet['BM130'] = list_date_issue_patent[0][0], list_date_issue_patent[0][1]
        sheet['BO130'], sheet['BQ130'] = list_date_issue_patent[0][2], list_date_issue_patent[0][3]

        list_columns_for_publisher = ['Q', 'S', 'U', 'W', 'Y', 'AA', 'AC', 'AE', 'AG', 'AI', 'AK', 'AM', 'AO', 'AQ',
                                      'AS', 'AU', 'AW', 'AY', 'BA', 'BC', 'BE', 'BG', 'BI', 'BK', 'BM', 'BO', 'BQ']
        list_columns_for_publisher_last = ['A', 'C', 'E', 'G', 'I', 'K', 'M', 'O', 'Q', 'S', 'U', 'W', 'Y', 'AA', 'AC',
                                           'AE', 'AG', 'AI', 'AK', 'AM', 'AO', 'AQ', 'AS', 'AU', 'AW', 'AY', 'BA', 'BC',
                                           'BE', 'BG', 'BI', 'BK', 'BM', 'BO', 'BQ']
        row = 132
        index_publisher_last = 0
        stop = False
        for symbol in issued_whom:
            if row == 135:
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
        sheet['P136'], sheet['R136'] = list_date_issue_patent[2][0], list_date_issue_patent[2][1]
        # Месяц
        sheet['U136'], sheet['W136'] = list_date_issue_patent[1][0], list_date_issue_patent[1][1]
        # Год
        sheet['Z136'], sheet['AB136'] = list_date_issue_patent[0][0], list_date_issue_patent[0][1]
        sheet['AD136'], sheet['AF136'] = list_date_issue_patent[0][2], list_date_issue_patent[0][3]

        date_end_patent = date_end_patent.split('-')
        # День
        sheet['AL136'], sheet['AN136'] = date_end_patent[2][0], date_end_patent[2][1]
        # Месяц
        sheet['AQ136'], sheet['AS136'] = date_end_patent[1][0], date_end_patent[1][1]
        # Город
        sheet['AV136'], sheet['AX136'] = date_end_patent[0][0], date_end_patent[0][1]
        sheet['AZ136'], sheet['BB136'] = date_end_patent[0][2], date_end_patent[0][3]
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

    row = 156
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
        sheet['A166'] = 'X'
    else:
        sheet['W166'] = 'X'

    arr_date = start_date.split('-')[::-1]
    # День
    sheet['AX171'] = arr_date[0][0]
    sheet['AZ171'] = arr_date[0][1]
    # Месяц
    sheet['BC171'] = arr_date[1][0]
    sheet['BE171'] = arr_date[1][1]
    # Год
    sheet['BH171'] = arr_date[2][0]
    sheet['BJ171'] = arr_date[2][1]
    sheet['BL171'] = arr_date[2][2]
    sheet['BN171'] = arr_date[2][3]

    row = 177
    index = 0
    for symbol in address:
        for col in range(index, len(list_columns)):
            cell = list_columns[index] + str(row)
            if list_columns[index] == 'BQ':
                sheet[f'{cell}'] = symbol
                if row == 180:
                    row += 3
                else:
                    row += 2
                index = 0
                break
            sheet[f'{cell}'] = symbol
            index += 1
            break

    sheet['AK190'] = full_name_director
    if person == 'person_proxy':
        try:
            full_name = data['full_name']
            passport_series = data['series']
            passport_number = data['number']
            date_issue = data['date_issue']
            issued_by = data['issued_by']

            sheet['AE200'] = full_name

            if len(passport_series) == 4:
                passport_series = passport_series[0] + passport_series[1] + ' ' + passport_series[2] + passport_series[3]
            sheet['G202'] = passport_series
            sheet['X202'] = passport_number
            date_issue = '.'.join(str(date_issue).split('-')[::-1])
            sheet['AR202'] = date_issue
            sheet['J204'] = issued_by
        except:
            pass

    else:
        if not DirectorOrganization.objects.filter(organization_id=organization_id).exists():
            raise CustomValidationError({'error': 'Нет данных о директоре компании'})

        sheet["AE200"] = full_name_director
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
        sheet["G202"] = passport_series
        sheet["X202"] = passport_number
        date_issue = '.'.join(str(date_issue).split('-')[::-1])
        sheet["AR202"] = date_issue
        sheet["J204"] = issued_whom

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="notice_conclusion.xlsx"'
    doc.save(response)
    return response
