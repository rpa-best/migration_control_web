from openpyxl import *
from django.http import HttpResponse
from v1_1.models.organization import Organization, DirectorOrganization
from v1_1.models.worker import DocumentsWorker, Worker
from .custom_handler import *
from v1_1.serializers.blanks import ArrivalNoticeSerializer


def GenerationArrivalNotice(data):
    # =========== Входные данные, которые вводятся пользователем вручную ===========
    worker_id = data['worker_id']
    document_type = data['document_type']
    purpose_departure = data['purpose_departure']
    position = data['position'].upper()
    duration_stay = data['duration_stay'].split('-')
    receiving_side = data['receiving_side']
    date_issue = str(data['date_issue']).split('-')
    validity_period = str(data['validity_period']).split('-')

    # Входные данные для второго листа
    # Адрес прежнего места пребывания
    address_former_place_residence = data['address_former_place_residence'].upper()

    # Место пребывания по адресу
    place_stay_region = str(data['place_stay_region'].upper())
    place_stay_area = str(data['place_stay_area'].upper())
    place_stay_city = str(data['place_stay_city'].upper())
    place_stay_street = str(data['place_stay_street'].upper())
    object_type = str(data['object_type'].upper())
    place_stay_house = data['place_stay_house']
    place_stay_frame = data['place_stay_frame']
    place_stay_structure = data['place_stay_structure']
    room_type = str(data['room_type'].upper())
    place_stay_apartment = data['place_stay_apartment']
    place_stay = data['place_stay']
    document_right_use = str(data['document_right_use'].upper())

    # ============ Данные, которые подтягиваются из базы данных ============
    # ФИО работника
    worker = Worker.objects.get(pk=worker_id)
    name_worker = worker.name.upper()
    surname_worker = worker.surname.upper()
    patronymic_worker = worker.patronymic
    citizenship_worker = worker.citizenship.upper()

    if worker.birthday is None:
        raise CustomValidationError({'error': 'У сотрудника не указана дата рождения'})

    birthday_worker = str(worker.birthday).split('-')

    if len(birthday_worker) == 0:
        raise CustomValidationError({'error': 'Не заполнена дата рождения сотрудника'})

    gender_worker = worker.gender
    place_birth_worker = worker.place_birth.upper()
    phone_worker = worker.phone
    identification_card_display = worker.get_identification_card_display().upper()
    if not DocumentsWorker.objects.filter(worker_id=worker, type_document=worker.identification_card,
                                                         archive=False).exists():
        raise CustomValidationError({'error': 'У сотрудника нет документа, удостоверяющий личность'})

    identification_card = DocumentsWorker.objects.filter(worker_id=worker, type_document=worker.identification_card,
                                                         archive=False)[0]

    identification_card_series = identification_card.series
    identification_card_number = identification_card.number
    identification_card_date_issue = str(identification_card.date_issue).split('-')
    identification_card_date_end = str(identification_card.date_end).split('-')

    path_file_doc = 'v1_1/document_templates/arrival_notice.xlsx'
    doc = load_workbook(path_file_doc)

    """Занесение данных в первый лист Excel файла"""
    sheet = doc['sheet 1']

    list_columns_name_worker = ['N', 'R', 'V', 'Z', 'AD', 'AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF', 'BJ', 'BN', 'BR',
                                'BV', 'BZ', 'CD', 'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']
    row = 12
    index = 0
    stop = False
    for symbol in surname_worker:
        for col in range(index, len(list_columns_name_worker)):
            cell = list_columns_name_worker[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'DN':
                stop = True
            break
        if stop is True:
            break

    row = 14
    index = 0
    stop = False
    for symbol in name_worker:
        for col in range(index, len(list_columns_name_worker)):
            cell = list_columns_name_worker[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'DN':
                stop = True
            break
        if stop is True:
            break

    if patronymic_worker:
        list_columns_patronymic_worker = ['Z', 'AD', 'AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF', 'BJ', 'BN', 'BR', 'BV', 'BZ', 'CD',
                                          'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']
        row = 16
        index = 0
        stop = False
        for symbol in patronymic_worker.upper():
            for col in range(index, len(list_columns_patronymic_worker)):
                cell = list_columns_patronymic_worker[index] + str(row)
                sheet[f'{cell}'] = symbol
                index += 1
                if col == 'DN':
                    stop = True
                break
            if stop is True:
                break

    list_columns_citizenship_worker = ['V', 'Z', 'AD', 'AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF', 'BJ', 'BN', 'BR', 'BV',
                                       'BZ', 'CD', 'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']
    row = 18
    index = 0
    stop = False
    for symbol in citizenship_worker:
        for col in range(index, len(list_columns_citizenship_worker)):
            cell = list_columns_citizenship_worker[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'DN':
                stop = True
            break
        if stop is True:
            break
    try:
        # День рождения
        sheet['AD21'], sheet['AH21'] = birthday_worker[2][0], birthday_worker[2][1]
        # Месяц рождения
        sheet['AT21'], sheet['AX21'] = birthday_worker[1][0], birthday_worker[1][1]
        # Год рождения
        sheet['BF21'] = birthday_worker[0][0]
        sheet['BJ21'] = birthday_worker[0][1]
        sheet['BN21'] = birthday_worker[0][2]
        sheet['BR21'] = birthday_worker[0][3]
    except:
        raise CustomValidationError({'error': 'У сотрудника не указана дата рождения'})

    if gender_worker == 'male':
        sheet['CL21'] = 'X'
    else:
        sheet['DB21'] = 'X'

    list_columns_place_birth_worker = ['Z', 'AD', 'AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF', 'BJ', 'BN', 'BR', 'BV', 'BZ',
                    'CD', 'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']
    row = 23
    index = 0
    for symbol in place_birth_worker:
        if row > 27:
            break
        for col in range(index, len(list_columns_place_birth_worker)):
            cell = list_columns_place_birth_worker[index] + str(row)
            if list_columns_place_birth_worker[index] == 'DN':
                sheet[f'{cell}'] = symbol
                row += 2
                index = 0
                break
            sheet[f'{cell}'] = symbol
            index += 1
            break

    list_columns_identification_card = ['J', 'N', 'R', 'V', 'Z', 'AD', 'AH', 'AL', 'AP', 'AT']
    row = 29
    index = 0
    stop = False
    for symbol in identification_card_display:
        for col in range(index, len(list_columns_identification_card)):
            cell = list_columns_identification_card[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'AT':
                stop = True
            break
        if stop is True:
            break

    list_columns = ['BF', 'BJ', 'BN', 'BR']

    row = 29
    index = 0
    stop = False
    for symbol in identification_card_series:
        for col in range(index, len(list_columns)):
            cell = list_columns[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'BR':
                stop = True
            break
        if stop is True:
            break

    list_columns = ['BZ', 'CD', 'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']

    row = 29
    index = 0
    stop = False
    for symbol in identification_card_number:
        for col in range(index, len(list_columns)):
            cell = list_columns[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'DN':
                stop = True
            break
        if stop is True:
            break

    # День
    sheet['I31'], sheet['M31'] = identification_card_date_issue[2][0], identification_card_date_issue[2][1]
    # Месяц
    sheet['Z31'], sheet['AD31'] = identification_card_date_issue[1][0], identification_card_date_issue[1][1]
    # Год
    sheet['AL31'] = identification_card_date_issue[0][0]
    sheet['AP31'] = identification_card_date_issue[0][1]
    sheet['AT31'] = identification_card_date_issue[0][2]
    sheet['AX31'] = identification_card_date_issue[0][3]

    # День
    sheet['BN31'], sheet['BR31'] = identification_card_date_end[2][0], identification_card_date_end[2][1]
    # Месяц
    sheet['CD31'], sheet['CH31'] = identification_card_date_end[1][0], identification_card_date_end[1][1]
    # Год
    sheet['CP31'] = identification_card_date_end[0][0]
    sheet['CT31'] = identification_card_date_end[0][1]
    sheet['CX31'] = identification_card_date_end[0][2]
    sheet['DB31'] = identification_card_date_end[0][3]

    if document_type == 'visa':
        sheet["H36"] = 'X'
    elif document_type == 'resident_card':
        sheet["AJ36"] = 'X'
    elif document_type == 'temporary_residence_permit':
        sheet["BT36"] = 'X'
    elif document_type == 'temporary_residence_permit_for_the_purpose_of_education':
        sheet["DD36"] = 'X'

    if document_type != 'not_documents':
        series = str(data['series'])
        number = str(data['number'])
        if len(series) == 4:
            sheet["J40"] = series[0]
            sheet["N40"] = series[1]
            sheet["R40"] = series[2]
            sheet["V40"] = series[3]
        elif len(series) == 3:
            sheet["J40"] = series[0]
            sheet["N40"] = series[1]
            sheet["R40"] = series[2]
        elif len(series) == 3:
            sheet["J40"] = series[0]
            sheet["N40"] = series[1]
            sheet["R40"] = series[2]
        else:
            sheet["J40"] = series[0]
            sheet["N40"] = series[1]

        if len(number) == 6:
            sheet["AD40"] = number[0]
            sheet["AH40"] = number[1]
            sheet["AL40"] = number[2]
            sheet["AP40"] = number[3]
            sheet["AT40"] = number[4]
            sheet["AX40"] = number[5]
        elif len(number) == 7:
            sheet["AD40"] = number[0]
            sheet["AH40"] = number[1]
            sheet["AL40"] = number[2]
            sheet["AP40"] = number[3]
            sheet["AT40"] = number[4]
            sheet["AX40"] = number[5]
            sheet["BB40"] = number[6]

    # День
    sheet['I42'], sheet['M42'] = date_issue[2][0], date_issue[2][1]
    # Месяц
    sheet['Z42'], sheet['AD42'] = date_issue[1][0], date_issue[1][1]
    # Год
    sheet['AL42'] = date_issue[0][0]
    sheet['AP42'] = date_issue[0][1]
    sheet['AT42'] = date_issue[0][2]
    sheet['AX42'] = date_issue[0][3]

    # День
    sheet['BN42'], sheet['BR42'] = validity_period[2][0], validity_period[2][1]
    # Месяц
    sheet['CD42'], sheet['CH42'] = validity_period[1][0], validity_period[1][1]
    # Год
    sheet['CP42'] = validity_period[0][0]
    sheet['CT42'] = validity_period[0][1]
    sheet['CX42'] = validity_period[0][2]
    sheet['DB42'] = validity_period[0][3]

    if purpose_departure == 'official':
        sheet["AD44"] = 'X'
    elif purpose_departure == 'tourism':
        sheet["AQ44"] = 'X'
    elif purpose_departure == 'business':
        sheet["BD44"] = 'X'
    elif purpose_departure == 'studies':
        sheet["BO44"] = 'X'
    elif purpose_departure == 'job':
        sheet["CA44"] = 'X'
    elif purpose_departure == 'private':
        sheet["CN44"] = 'X'
    elif purpose_departure == 'transit':
        sheet["DB44"] = 'X'
    elif purpose_departure == 'humanitarian':
        sheet["AD46"] = 'X'
    else:
        sheet["AP46"] = 'X'

    if phone_worker is not None and phone_worker != '':
        trans_table = {ord('('): None, ord(')'): None, ord(' '): None, ord('-'): None,  ord('+'): None}
        phone_worker = phone_worker.translate(trans_table)
        phone_worker = phone_worker.replace('+', '')
        sheet["CD46"] = phone_worker[1]
        sheet["CH46"] = phone_worker[2]
        sheet["CL46"] = phone_worker[3]
        sheet["CP46"] = phone_worker[4]
        sheet["CT46"] = phone_worker[5]
        sheet["CX46"] = phone_worker[6]
        sheet["DB46"] = phone_worker[7]
        sheet["DF46"] = phone_worker[8]
        sheet["DJ46"] = phone_worker[9]
        sheet["DN46"] = phone_worker[10]

    list_columns = ['R', 'V', 'Z', 'AD', 'AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF', 'BJ', 'BN', 'BR', 'BV', 'BZ', 'CD',
                    'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']
    row = 48
    index = 0
    stop = False
    for symbol in position:
        for col in range(index, len(list_columns)):
            cell = list_columns[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'DN':
                stop = True
            break
        if stop is True:
            break

    if not DocumentsWorker.objects.filter(worker_id=worker_id, type_document='migration_card', archive=False).exists():
        raise CustomValidationError({'error': 'У работника нет актуальной миграционной карты'})

    migration_card = DocumentsWorker.objects.filter(worker_id=worker_id, type_document='migration_card', archive=False)[0]
    departure_date = str(migration_card.date_issue).split('-')

    # День выезда
    sheet['I50'], sheet['M50'] = departure_date[2][0], departure_date[2][1]
    # Месяц выезда
    sheet['Z50'], sheet['AD50'] = departure_date[1][0], departure_date[1][1]
    # Год выезда
    sheet['AL50'] = departure_date[0][0]
    sheet['AP50'] = departure_date[0][1]
    sheet['AT50'] = departure_date[0][2]
    sheet['AX50'] = departure_date[0][3]

    # Срок пребывания
    # День
    sheet['BN50'], sheet['BR50'] = duration_stay[2][0], duration_stay[2][1]
    # Месяц
    sheet['CD50'], sheet['CH50'] = duration_stay[1][0], duration_stay[1][1]
    # Год
    sheet['CP50'] = duration_stay[0][0]
    sheet['CT50'] = duration_stay[0][1]
    sheet['CX50'] = duration_stay[0][2]
    sheet['DB50'] = duration_stay[0][3]

    migration_card_series = migration_card.series
    migration_card_number = migration_card.number

    if migration_card_series:
        list_columns_migration_series = ['AP', 'AT', 'AX', 'BB']

        row = 52
        index = 0
        stop = False
        for symbol in migration_card_series:
            for col in range(index, len(list_columns_migration_series)):
                cell = list_columns_migration_series[index] + str(row)
                sheet[f'{cell}'] = symbol
                index += 1
                if col == 'BB':
                    stop = True
                break
            if stop is True:
                break
    else:
        raise CustomValidationError({'error': 'У работника в миграционной карте не указана серия'})

    list_columns_migration_number = ['BJ', 'BN', 'BR', 'BV', 'BZ', 'CD', 'CH', 'CL', 'CP', 'CT', 'CX']

    row = 52
    index = 0
    stop = False
    for symbol in migration_card_number:
        for col in range(index, len(list_columns_migration_number)):
            cell = list_columns_migration_number[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'CX':
                stop = True
            break
        if stop is True:
            break

    """Занесение данных в второй лист Excel файла"""
    sheet = doc['sheet 2']

    list_columns_for_address_former_place_residence = ['Z', 'AD', 'AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF',
                                                       'BJ', 'BN', 'BR', 'BV', 'BZ', 'CD', 'CH', 'CL', 'CP', 'CT',
                                                       'CX', 'DB', 'DF', 'DJ', 'DN']
    list_columns_for_address_former_place_residence_last = ['B', 'F', 'J', 'N', 'R', 'V', 'Z', 'AD', 'AH', 'AL', 'AP',
                                                            'AT', 'AX', 'BB', 'BF', 'BJ', 'BN', 'BR', 'BV', 'BZ', 'CD',
                                                            'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']
    row = 3
    index_address_former_place_residence_last = 0
    stop = False
    index = 0
    for symbol in address_former_place_residence:
        if row == 9:
            for col in range(index_address_former_place_residence_last, len(list_columns_for_address_former_place_residence_last)):
                cell = list_columns_for_address_former_place_residence_last[index_address_former_place_residence_last] + str(row)
                sheet[f'{cell}'] = symbol
                index_address_former_place_residence_last += 1
                if col == 'DN':
                    stop = True
                break
            if stop is True:
                break
        else:
            for col in range(index, len(list_columns_for_address_former_place_residence)):
                cell = list_columns_for_address_former_place_residence[index] + str(row)
                if list_columns_for_address_former_place_residence[index] == 'DN':
                    sheet[f'{cell}'] = symbol
                    row += 2
                    index = 0
                    break
                sheet[f'{cell}'] = symbol
                index += 1
                break

        # ============== 2. СВЕДЕНИЯ О МЕСТЕ ПРЕБЫВАНИЯ ==============
    list_columns = ['V', 'Z', 'AD', 'AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF', 'BJ', 'BN', 'BR', 'BV', 'BZ',
                    'CD', 'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']
    row = 14
    index = 0
    for symbol in place_stay_region:
        for col in range(index, len(list_columns)):
            cell = list_columns[index] + str(row)
            if list_columns[index] == 'DN':
                sheet[f'{cell}'] = symbol
                row += 2
                index = 0
                break
            sheet[f'{cell}'] = symbol
            index += 1
            break

    list_columns = ['V', 'Z', 'AD', 'AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF', 'BJ', 'BN', 'BR', 'BV', 'BZ',
                    'CD', 'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']
    row = 18
    index = 0
    stop = False
    for symbol in place_stay_area:
        for col in range(index, len(list_columns)):
            cell = list_columns[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'DN':
                stop = True
            break
        if stop is True:
            break

    list_columns = ['Z', 'AD', 'AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF', 'BJ', 'BN', 'BR', 'BV', 'BZ',
                    'CD', 'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']
    row = 20
    index = 0
    stop = False
    for symbol in place_stay_city:
        for col in range(index, len(list_columns)):
            cell = list_columns[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'DN':
                stop = True
            break
        if stop is True:
            break

    list_columns = ['V', 'Z', 'AD', 'AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF', 'BJ', 'BN', 'BR', 'BV', 'BZ',
                    'CD', 'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']
    row = 22
    index = 0
    stop = False
    for symbol in place_stay_street:
        for col in range(index, len(list_columns)):
            cell = list_columns[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'DN':
                stop = True
            break
        if stop is True:
            break

    sheet['B24'] = object_type

    list_columns = ['AD', 'AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF']
    row = 24
    index = 0
    stop = False
    for symbol in place_stay_house:  # Заполнение дома
        for col in range(index, len(list_columns)):
            cell = list_columns[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'BF':
                stop = True
            break
        if stop is True:
            break

    list_columns = ['BR', 'BV', 'BZ', 'CD', 'CH']
    row = 24
    index = 0
    stop = False
    for symbol in place_stay_frame:  # Заполнение корпуса
        for col in range(index, len(list_columns)):
            cell = list_columns[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'CH':
                stop = True
            break
        if stop is True:
            break

    list_columns = ['CX', 'DB', 'DF', 'DJ']
    row = 24
    index = 0
    stop = False
    for symbol in place_stay_structure:  # Заполнение строения
        for col in range(index, len(list_columns)):
            cell = list_columns[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'DJ':
                stop = True
            break
        if stop is True:
            break

    sheet['B26'] = room_type

    list_columns = ['AJ', 'AN', 'AR', 'AV']
    row = 26
    index = 0
    stop = False
    for symbol in place_stay_apartment:  # Заполнение квартиры/офиса
        for col in range(index, len(list_columns)):
            cell = list_columns[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'AV':
                stop = True
            break
        if stop is True:
            break

    if place_stay == 'residential_premises':
        sheet['Y28'] = 'X'
    elif place_stay == 'residential_premises':
        sheet['AZ28'] = 'X'
    else:
        sheet['CB28'] = 'X'

    list_columns = ['AL', 'AP', 'AT', 'AX', 'BB', 'BF', 'BJ', 'BN', 'BR', 'BV', 'BZ',
                    'CD', 'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']

    row = 31
    index = 0
    for symbol in document_right_use:
        for col in range(index, len(list_columns)):
            cell = list_columns[index] + str(row)
            if list_columns[index] == 'DN':
                sheet[f'{cell}'] = symbol
                row += 2
                if row == 37:
                    break
                index = 0
                break
            sheet[f'{cell}'] = symbol
            index += 1
            break

    """Занесение данных в третий лист Excel файла"""

    sheet = doc["sheet 3"]

    # ================== Выбор стороны ==================
    if receiving_side == 'legal_entity':
        sheet["CP3"] = 'X'

        organization_id = Worker.objects.get(pk=worker_id).organization_id

        # ФИО директора организации
        director = DirectorOrganization.objects.get(organization_id=organization_id)
        name_director = director.name_director.upper()
        surname_director = director.surname_director.upper()
        patronymic_director = director.patronymic_director

        # Паспортные данные директора
        passport_series_director = director.passport_series.upper()
        passport_number_director = director.passport_number.upper()
        date_issue_passport_director = director.date_issue_passport
        date_end_passport_director = director.date_end_passport

        list_columns = ['N', 'R', 'V', 'Z', 'AD', 'AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF', 'BJ', 'BN', 'BR', 'BV', 'BZ',
                        'CD', 'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']

        row = 5
        index = 0
        stop = False
        for symbol in surname_director:
            for col in range(index, len(list_columns)):
                cell = list_columns[index] + str(row)
                sheet[f'{cell}'] = symbol
                index += 1
                if col == 'DN':
                    stop = True
                break
            if stop is True:
                break

        row = 7
        index = 0
        stop = False
        for symbol in name_director:
            for col in range(index, len(list_columns)):
                cell = list_columns[index] + str(row)
                sheet[f'{cell}'] = symbol
                index += 1
                if col == 'DN':
                    stop = True
                break
            if stop is True:
                break

        if patronymic_director:
            list_columns = ['AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF', 'BJ', 'BN', 'BR', 'BV', 'BZ', 'CD', 'CH', 'CL',
                            'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']
            row = 9
            index = 0
            stop = False
            for symbol in patronymic_director.upper():
                for col in range(index, len(list_columns)):
                    cell = list_columns[index] + str(row)
                    sheet[f'{cell}'] = symbol
                    index += 1
                    if col == 'DN':
                        stop = True
                    break
                if stop is True:
                    break

        list_columns = ['F', 'J', 'N', 'R', 'V', 'Z', 'AD', 'AH', 'AL', 'AP', 'AT']

        row = 11
        index = 0
        stop = False
        for symbol in 'ПАСПОРТ':
            for col in range(index, len(list_columns)):
                cell = list_columns[index] + str(row)
                sheet[f'{cell}'] = symbol
                index += 1
                if col == 'AT':
                    stop = True
                break
            if stop is True:
                break

        list_columns = ['BF', 'BJ', 'BN', 'BR']
        row = 11
        index = 0
        stop = False
        for symbol in passport_series_director:
            for col in range(index, len(list_columns)):
                cell = list_columns[index] + str(row)
                sheet[f'{cell}'] = symbol
                index += 1
                if col == 'BR':
                    stop = True
                break
            if stop is True:
                break

        list_columns = ['BZ', 'CD', 'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']
        row = 11
        index = 0
        stop = False
        for symbol in passport_number_director:
            for col in range(index, len(list_columns)):
                cell = list_columns[index] + str(row)
                sheet[f'{cell}'] = symbol
                index += 1
                if col == 'DN':
                    stop = True
                break
            if stop is True:
                break

        date_issue_passport_director = str(date_issue_passport_director).split('-')
        # День
        sheet["I13"], sheet["M13"] = date_issue_passport_director[2][0], date_issue_passport_director[2][1]
        # Месяц
        sheet["Z13"], sheet["AD13"] = date_issue_passport_director[1][0], date_issue_passport_director[1][1]
        # Год
        sheet["AL13"] = date_issue_passport_director[0][0]
        sheet["AP13"] = date_issue_passport_director[0][1]
        sheet["AT13"] = date_issue_passport_director[0][2]
        sheet["AX13"] = date_issue_passport_director[0][3]

        date_end_passport_director = str(date_end_passport_director).split('-')
        # День
        sheet["BN13"], sheet["BR13"] = date_end_passport_director[2][0], date_end_passport_director[2][1]
        # Месяц
        sheet["CD13"], sheet["CH13"] = date_end_passport_director[1][0], date_end_passport_director[1][1]
        # Год
        sheet['CP13'] = date_end_passport_director[0][0]
        sheet['CT13'] = date_end_passport_director[0][1]
        sheet['CX13'] = date_end_passport_director[0][2]
        sheet['DB13'] = date_end_passport_director[0][3]
    else:
        # ========================================== Физическое лицо =============================================
        sheet["DN3"] = 'X'

        surname_receiving_side = data['surname_receiving_side'].upper()
        list_columns = ['N', 'R', 'V', 'Z', 'AD', 'AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF', 'BJ', 'BN', 'BR', 'BV', 'BZ',
                        'CD', 'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']
        row = 5
        index = 0
        stop = False
        for symbol in surname_receiving_side:
            for col in range(index, len(list_columns)):
                cell = list_columns[index] + str(row)
                sheet[f'{cell}'] = symbol
                index += 1
                if col == 'DN':
                    stop = True
                break
            if stop is True:
                break

        name_receiving_side = data['name_receiving_side'].upper()
        row = 7
        index = 0
        stop = False
        for symbol in name_receiving_side:
            for col in range(index, len(list_columns)):
                cell = list_columns[index] + str(row)
                sheet[f'{cell}'] = symbol
                index += 1
                if col == 'DN':
                    stop = True
                break
            if stop is True:
                break

        patronymic_receiving_side = data['patronymic_receiving_side'].upper()
        list_columns = ['AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF', 'BJ', 'BN', 'BR', 'BV', 'BZ', 'CD', 'CH', 'CL',
                        'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']
        row = 9
        index = 0
        stop = False
        for symbol in patronymic_receiving_side:
            for col in range(index, len(list_columns)):
                cell = list_columns[index] + str(row)
                sheet[f'{cell}'] = symbol
                index += 1
                if col == 'DN':
                    stop = True
                break
            if stop is True:
                break

        type_of_identity_document_mapping = dict(ArrivalNoticeSerializer.IDENTIFICATION_CARD)
        type_of_identity_document = type_of_identity_document_mapping.get(data['type_of_identity_document']).upper()

        list_columns = ['F', 'J', 'N', 'R', 'V', 'Z', 'AD', 'AH', 'AL', 'AP', 'AT']

        row = 11
        index = 0
        stop = False
        for symbol in type_of_identity_document:
            for col in range(index, len(list_columns)):
                cell = list_columns[index] + str(row)
                sheet[f'{cell}'] = symbol
                index += 1
                if col == 'AT':
                    stop = True
                break
            if stop is True:
                break

        series_receiving_side = data['series_receiving_side'].upper()
        list_columns = ['BF', 'BJ', 'BN', 'BR']

        row = 11
        index = 0
        stop = False
        for symbol in series_receiving_side:
            for col in range(index, len(list_columns)):
                cell = list_columns[index] + str(row)
                sheet[f'{cell}'] = symbol
                index += 1
                if col == 'BR':
                    stop = True
                break
            if stop is True:
                break

        number_receiving_side = data['number_receiving_side'].upper()
        list_columns = ['BZ', 'CD', 'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']

        row = 11
        index = 0
        stop = False
        for symbol in number_receiving_side:
            for col in range(index, len(list_columns)):
                cell = list_columns[index] + str(row)
                sheet[f'{cell}'] = symbol
                index += 1
                if col == 'DN':
                    stop = True
                break
            if stop is True:
                break

        date_issue_receiving_side = data['date_issue_receiving_side'].split('-')
        # День
        sheet["I13"], sheet["M13"] = date_issue_receiving_side[2][0], date_issue_receiving_side[2][1]
        # Месяц
        sheet["Z13"], sheet["AD13"] = date_issue_receiving_side[1][0], date_issue_receiving_side[1][1]
        # Год
        sheet["AL13"] = date_issue_receiving_side[0][0]
        sheet["AP13"] = date_issue_receiving_side[0][1]
        sheet["AT13"] = date_issue_receiving_side[0][2]
        sheet["AX13"] = date_issue_receiving_side[0][3]

        sell_by_receiving_side = data['sell_by_receiving_side'].split('-')
        # День
        sheet["BN13"], sheet["BR13"] = sell_by_receiving_side[2][0], sell_by_receiving_side[2][1]
        # Месяц
        sheet["CD13"], sheet["CH13"] = sell_by_receiving_side[1][0], sell_by_receiving_side[1][1]
        # Год
        sheet["CP13"] = sell_by_receiving_side[0][0]
        sheet["CT13"] = sell_by_receiving_side[0][1]
        sheet["CX13"] = sell_by_receiving_side[0][2]
        sheet["DB13"] = sell_by_receiving_side[0][3]

        # ============== Место жительство ==============
        region = data['region'].upper()
        list_columns = ['Z', 'AD', 'AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF', 'BJ', 'BN', 'BR', 'BV', 'BZ',
                        'CD', 'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']
        row = 17
        index = 0
        for symbol in region:
            for col in range(index, len(list_columns)):
                cell = list_columns[index] + str(row)
                if list_columns[index] == 'DN':
                    sheet[f'{cell}'] = symbol
                    row += 2
                    index = 0
                    break
                sheet[f'{cell}'] = symbol
                index += 1
                break

        area = data['area'].upper()
        list_columns = ['V', 'Z', 'AD', 'AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF', 'BJ', 'BN', 'BR', 'BV', 'BZ',
                        'CD', 'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']
        row = 21
        index = 0
        stop = False
        for symbol in area:
            for col in range(index, len(list_columns)):
                cell = list_columns[index] + str(row)
                sheet[f'{cell}'] = symbol
                index += 1
                if col == 'DN':
                    stop = True
                break
            if stop is True:
                break

        city = data['city'].upper()
        list_columns = ['AD', 'AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF', 'BJ', 'BN', 'BR', 'BV', 'BZ',
                        'CD', 'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']
        row = 23
        index = 0
        stop = False
        for symbol in city:
            for col in range(index, len(list_columns)):
                cell = list_columns[index] + str(row)
                sheet[f'{cell}'] = symbol
                index += 1
                if col == 'DN':
                    stop = True
                break
            if stop is True:
                break

        street = data['street'].upper()
        list_columns = ['V', 'Z', 'AD', 'AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF', 'BJ', 'BN', 'BR', 'BV', 'BZ',
                        'CD', 'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']
        row = 25
        index = 0
        stop = False
        for symbol in street:
            for col in range(index, len(list_columns)):
                cell = list_columns[index] + str(row)
                sheet[f'{cell}'] = symbol
                index += 1
                if col == 'DN':
                    stop = True
                break
            if stop is True:
                break

        house = data['house'].upper()
        list_columns = ['J', 'N', 'R', 'V']
        row = 27
        index = 0
        stop = False
        for symbol in house:
            for col in range(index, len(list_columns)):
                cell = list_columns[index] + str(row)
                sheet[f'{cell}'] = symbol
                index += 1
                if col == 'V':
                    stop = True
                break
            if stop is True:
                break

        frame = data['frame'].upper()
        list_columns = ['AH', 'AL', 'AP', 'AT', 'AX']
        row = 27
        index = 0
        stop = False
        for symbol in frame:
            for col in range(index, len(list_columns)):
                cell = list_columns[index] + str(row)
                sheet[f'{cell}'] = symbol
                index += 1
                if col == 'AX':
                    stop = True
                break
            if stop is True:
                break

        structure = data['structure'].upper()
        list_columns = ['BN', 'BR', 'BV', 'BZ']
        row = 27
        index = 0
        stop = False
        for symbol in structure:
            for col in range(index, len(list_columns)):
                cell = list_columns[index] + str(row)
                sheet[f'{cell}'] = symbol
                index += 1
                if col == 'BZ':
                    stop = True
                break
            if stop is True:
                break

        apartment = data['apartment'].upper()
        list_columns = ['CP', 'CT', 'CX', 'DB']
        row = 27
        index = 0
        stop = False
        for symbol in apartment:
            for col in range(index, len(list_columns)):
                cell = list_columns[index] + str(row)
                sheet[f'{cell}'] = symbol
                index += 1
                if col == 'DB':
                    stop = True
                break
            if stop is True:
                break

    list_columns_name_worker = ['N', 'R', 'V', 'Z', 'AD', 'AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF', 'BJ', 'BN', 'BR',
                                'BV', 'BZ', 'CD', 'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']
    row = 31
    index = 0
    stop = False
    for symbol in surname_worker:
        for col in range(index, len(list_columns_name_worker)):
            cell = list_columns_name_worker[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'DN':
                stop = True
            break
        if stop is True:
            break

    row = 33
    index = 0
    stop = False
    for symbol in name_worker:
        for col in range(index, len(list_columns_name_worker)):
            cell = list_columns_name_worker[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'DN':
                stop = True
            break
        if stop is True:
            break

    if patronymic_worker:
        list_columns_patronymic_worker = ['AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF', 'BJ', 'BN', 'BR', 'BV', 'BZ', 'CD',
                                          'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']
        row = 35
        index = 0
        stop = False
        for symbol in patronymic_worker.upper():
            for col in range(index, len(list_columns_patronymic_worker)):
                cell = list_columns_patronymic_worker[index] + str(row)
                sheet[f'{cell}'] = symbol
                index += 1
                if col == 'DN':
                    stop = True
                break
            if stop is True:
                    break

    list_columns_citizenship_worker = ['R', 'V', 'Z', 'AD', 'AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF', 'BJ', 'BN', 'BR',
                                'BV', 'BZ', 'CD', 'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']
    row = 37
    index = 0
    stop = False
    for symbol in citizenship_worker:
        for col in range(index, len(list_columns_citizenship_worker)):
            cell = list_columns_citizenship_worker[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'DN':
                stop = True
            break
        if stop is True:
            break

    # День
    sheet['AA39'], sheet['AE39'] = birthday_worker[2][0], birthday_worker[2][1]
    # Месяц
    sheet['AQ39'], sheet['AU39'] = birthday_worker[1][0], birthday_worker[1][1]
    # Год
    sheet['BC39'] = birthday_worker[0][0]
    sheet['BG39'] = birthday_worker[0][1]
    sheet['BK39'] = birthday_worker[0][2]
    sheet['BO39'] = birthday_worker[0][3]

    if gender_worker == 'male':
        sheet['CL39'] = 'X'
    else:
        sheet['DB39'] = 'X'

    list_columns_place_birth_worker = ['Z', 'AD', 'AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF', 'BJ', 'BN', 'BR', 'BV', 'BZ',
                    'CD', 'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']
    row = 41
    index = 0
    for symbol in place_birth_worker:
        if row > 45:
            break
        for col in range(index, len(list_columns_place_birth_worker)):
            cell = list_columns_place_birth_worker[index] + str(row)
            if list_columns_place_birth_worker[index] == 'DN':
                sheet[f'{cell}'] = symbol
                row += 2
                index = 0
                break
            sheet[f'{cell}'] = symbol
            index += 1
            break

    list_columns_identification_card = ['F', 'J', 'N', 'R', 'V', 'Z', 'AD', 'AH', 'AL', 'AP', 'AT']
    row = 47
    index = 0
    stop = False
    for symbol in identification_card_display:
        for col in range(index, len(list_columns_identification_card)):
            cell = list_columns_identification_card[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'AT':
                stop = True
            break
        if stop is True:
            break

    list_columns = ['BF', 'BJ', 'BN', 'BR']

    row = 47
    index = 0
    stop = False
    for symbol in identification_card_series:
        for col in range(index, len(list_columns)):
            cell = list_columns[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'BR':
                stop = True
            break
        if stop is True:
            break

    list_columns = ['BZ', 'CD', 'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']

    row = 47
    index = 0
    stop = False
    for symbol in identification_card_number:
        for col in range(index, len(list_columns)):
            cell = list_columns[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'DN':
                stop = True
            break
        if stop is True:
            break

    # День
    sheet['I49'], sheet['M49'] = identification_card_date_issue[2][0], identification_card_date_issue[2][1]
    # Месяц
    sheet['Z49'], sheet['AD49'] = identification_card_date_issue[1][0], identification_card_date_issue[1][1]
    # Год
    sheet['AL49'] = identification_card_date_issue[0][0]
    sheet['AP49'] = identification_card_date_issue[0][1]
    sheet['AT49'] = identification_card_date_issue[0][2]
    sheet['AX49'] = identification_card_date_issue[0][3]

    # День
    sheet['BN49'], sheet['BR49'] = identification_card_date_end[2][0], identification_card_date_end[2][1]
    # Месяц
    sheet['CD49'], sheet['CH49'] = identification_card_date_end[1][0], identification_card_date_end[1][1]
    # Год
    sheet['CP49'] = identification_card_date_end[0][0]
    sheet['CT49'] = identification_card_date_end[0][1]
    sheet['CX49'] = identification_card_date_end[0][2]
    sheet['DB49'] = identification_card_date_end[0][3]

    # ============== Место пребывания по адресу ==============
    list_columns = ['V', 'Z', 'AD', 'AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF', 'BJ', 'BN', 'BR', 'BV', 'BZ',
                    'CD', 'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']
    row = 53
    index = 0
    for symbol in place_stay_region:
        for col in range(index, len(list_columns)):
            cell = list_columns[index] + str(row)
            if list_columns[index] == 'DN':
                sheet[f'{cell}'] = symbol
                row += 2
                index = 0
                break
            sheet[f'{cell}'] = symbol
            index += 1
            break

    list_columns = ['V', 'Z', 'AD', 'AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF', 'BJ', 'BN', 'BR', 'BV', 'BZ',
                    'CD', 'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']
    row = 57
    index = 0
    stop = False
    for symbol in place_stay_area:
        for col in range(index, len(list_columns)):
            cell = list_columns[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'DN':
                stop = True
            break
        if stop is True:
            break

    list_columns = ['AD', 'AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF', 'BJ', 'BN', 'BR', 'BV', 'BZ',
                    'CD', 'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']
    row = 59
    index = 0
    stop = False
    for symbol in place_stay_city:
        for col in range(index, len(list_columns)):
            cell = list_columns[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'DN':
                stop = True
            break
        if stop is True:
            break

    list_columns = ['V', 'Z', 'AD', 'AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF', 'BJ', 'BN', 'BR', 'BV', 'BZ',
                    'CD', 'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']
    row = 61
    index = 0
    stop = False
    for symbol in place_stay_street:
        for col in range(index, len(list_columns)):
            cell = list_columns[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'DN':
                stop = True
            break
        if stop is True:
            break

    sheet['B63'] = object_type

    list_columns = ['AD', 'AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF']
    row = 63
    index = 0
    stop = False
    for symbol in place_stay_house:      # Заполнение дома
        for col in range(index, len(list_columns)):
            cell = list_columns[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'BF':
                stop = True
            break
        if stop is True:
            break

    list_columns = ['BR', 'BV', 'BZ', 'CD', 'CH']
    row = 63
    index = 0
    stop = False
    for symbol in place_stay_frame:      # Заполнение корпуса
        for col in range(index, len(list_columns)):
            cell = list_columns[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'CH':
                stop = True
            break
        if stop is True:
            break

    list_columns = ['CX', 'DB', 'DF', 'DJ']
    row = 63
    index = 0
    stop = False
    for symbol in place_stay_structure:     # Заполнение строения
        for col in range(index, len(list_columns)):
            cell = list_columns[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'DJ':
                stop = True
            break
        if stop is True:
            break

    sheet['B65'] = room_type

    list_columns = ['AJ', 'AN', 'AR', 'AV']
    row = 65
    index = 0
    stop = False
    for symbol in place_stay_apartment:      # Заполнение квартиры/офиса
        for col in range(index, len(list_columns)):
            cell = list_columns[index] + str(row)
            sheet[f'{cell}'] = symbol
            index += 1
            if col == 'AV':
                stop = True
            break
        if stop is True:
            break

    """Занесение данных в четвертый лист Excel файла"""
    sheet = doc["sheet 4"]

    if receiving_side == 'legal_entity':
        organization_id = Worker.objects.get(pk=worker_id).organization_id
        organization = Organization.objects.get(pk=organization_id)
        organization_name = f'{organization.get_organizational_form_display()} {organization.name}'.upper()
        organization_inn = organization.inn
        organization_address = organization.legal_address.upper()
        organization_phone = organization.phone

        if organization_phone[0] == '+':
            organization_phone = organization_phone[2:]
        elif organization_phone[0] == '7':
            organization_phone = organization_phone[1:]

        list_columns = ['Z', 'AD', 'AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF', 'BJ']
        row = 3
        index = 0
        stop = False
        for symbol in organization_phone:  # телефона принимающей стороны (организации)
            for col in range(index, len(list_columns)):
                cell = list_columns[index] + str(row)
                sheet[f'{cell}'] = symbol
                index += 1
                if col == 'BJ':
                    stop = True
                break
            if stop is True:
                break

        list_columns_for_organization_name = ['V', 'Z', 'AD', 'AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF', 'BJ', 'BN', 'BR',
                                              'BV', 'BZ', 'CD', 'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']
        list_columns_for_organization_name_last = ['B', 'F', 'J', 'N', 'R', 'V', 'Z', 'AD', 'AH', 'AL', 'AP', 'AT',
                                                   'AX', 'BB', 'BF', 'BJ', 'BN']
        row = 5
        index_organization_name_last = 0
        stop = False
        index = 0
        for symbol in organization_name:
            if row == 7:
                for col in range(index_organization_name_last,
                                 len(list_columns_for_organization_name_last)):
                    cell = list_columns_for_organization_name_last[index_organization_name_last] + str(row)
                    sheet[f'{cell}'] = symbol
                    if col == 'BN':
                        stop = True
                    break
                if stop is True:
                    break
            else:
                for col in range(index, len(list_columns_for_organization_name)):
                    cell = list_columns_for_organization_name[index] + str(row)
                    if list_columns_for_organization_name[index] == 'DN':
                        row += 2
                        break
                    sheet[f'{cell}'] = symbol
                    index += 1
                    break

        list_columns = ['BZ', 'CD', 'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']
        row = 7
        index = 0
        stop = False
        for symbol in organization_inn:  # телефона принимающей стороны (организации)
            for col in range(index, len(list_columns)):
                cell = list_columns[index] + str(row)
                sheet[f'{cell}'] = symbol
                index += 1
                if list_columns[col] == 'DN':
                    stop = True
                break
            if stop is True:
                break

        list_columns_for_organization_address = ['Z', 'AD', 'AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF', 'BJ', 'BN',
                                              'BR', 'BV', 'BZ', 'CD', 'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF',
                                                 'DJ', 'DN']
        list_columns_for_organization_address_last = ['B', 'F', 'J', 'N', 'R', 'V', 'Z', 'AD', 'AH', 'AL', 'AP',
                                                      'AT', 'AX', 'BB', 'BF', 'BJ', 'BN', 'BR', 'BV', 'BZ', 'CD',
                                                      'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']
        row = 9
        index_organization_address_last = 0
        stop = False
        index = 0
        for symbol in organization_address:
            if row == 9:
                for col in range(index, len(list_columns_for_organization_address)):
                    cell = list_columns_for_organization_address[index] + str(row)
                    sheet[f'{cell}'] = symbol
                    if list_columns_for_organization_address[index] == 'DN':
                        row += 2
                        break
                    index += 1
                    break
            elif row == 11:
                for col in range(index_organization_address_last,
                                 len(list_columns_for_organization_address_last)):
                    cell = list_columns_for_organization_address_last[index_organization_address_last] + str(row)
                    sheet[f'{cell}'] = symbol
                    index_organization_address_last += 1
                    if list_columns_for_organization_address_last[index_organization_address_last - 1] == 'DN':
                        row += 2
                        index_organization_address_last = 0
                    break
            elif row == 13:
                for col in range(index_organization_address_last,
                                 len(list_columns_for_organization_address_last)):
                    cell = list_columns_for_organization_address_last[index_organization_address_last] + str(row)
                    sheet[f'{cell}'] = symbol
                    index_organization_address_last += 1
                    if list_columns_for_organization_address_last[index_organization_address_last - 1] == 'DN':
                        row += 2
                        stop = True
                    break

            if stop is True:
                break

        list_columns = ['N', 'R', 'V', 'Z', 'AD', 'AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF', 'BJ', 'BN', 'BR', 'BV',
                        'BZ',
                        'CD', 'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']

        row = 27
        index = 0
        stop = False
        for symbol in surname_director:
            for col in range(index, len(list_columns)):
                cell = list_columns[index] + str(row)
                sheet[f'{cell}'] = symbol
                index += 1
                if col == 'DN':
                    stop = True
                break
            if stop is True:
                break

        row = 29
        index = 0
        stop = False
        for symbol in name_director:
            for col in range(index, len(list_columns)):
                cell = list_columns[index] + str(row)
                sheet[f'{cell}'] = symbol
                index += 1
                if col == 'DN':
                    stop = True
                break
            if stop is True:
                break

        if patronymic_director:
            list_columns = ['Z', 'AD', 'AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF', 'BJ', 'BN', 'BR', 'BV', 'BZ', 'CD',
                            'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']
            row = 31
            index = 0
            stop = False
            for symbol in patronymic_director.upper():
                for col in range(index, len(list_columns)):
                    cell = list_columns[index] + str(row)
                    sheet[f'{cell}'] = symbol
                    index += 1
                    if col == 'DN':
                        stop = True
                    break
                if stop is True:
                    break

        row = 33
        index_organization_name_last = 0
        stop = False
        index = 0
        for symbol in organization_name:
            if row == 35:
                for col in range(index_organization_name_last,
                                 len(list_columns_for_organization_name_last)):
                    cell = list_columns_for_organization_name_last[index_organization_name_last] + str(row)
                    sheet[f'{cell}'] = symbol
                    if col == 'BN':
                        stop = True
                    break
                if stop is True:
                    break
            else:
                for col in range(index, len(list_columns_for_organization_name)):
                    cell = list_columns_for_organization_name[index] + str(row)
                    if list_columns_for_organization_name[index] == 'DN':
                        row += 2
                        break
                    sheet[f'{cell}'] = symbol
                    index += 1
                    break

        list_columns = ['BZ', 'CD', 'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']
        row = 35
        index = 0
        stop = False
        for symbol in organization_inn:  # телефона принимающей стороны (организации)
            for col in range(index, len(list_columns)):
                cell = list_columns[index] + str(row)
                sheet[f'{cell}'] = symbol
                index += 1
                if list_columns[col] == 'DN':
                    stop = True
                break
            if stop is True:
                break
    else:
        list_columns = ['N', 'R', 'V', 'Z', 'AD', 'AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF', 'BJ', 'BN', 'BR', 'BV',
                        'BZ',
                        'CD', 'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']

        row = 27
        index = 0
        stop = False
        for symbol in surname_receiving_side:
            for col in range(index, len(list_columns)):
                cell = list_columns[index] + str(row)
                sheet[f'{cell}'] = symbol
                index += 1
                if col == 'DN':
                    stop = True
                break
            if stop is True:
                break

        row = 29
        index = 0
        stop = False
        for symbol in name_receiving_side:
            for col in range(index, len(list_columns)):
                cell = list_columns[index] + str(row)
                sheet[f'{cell}'] = symbol
                index += 1
                if col == 'DN':
                    stop = True
                break
            if stop is True:
                break

        if patronymic_receiving_side:
            list_columns = ['Z', 'AD', 'AH', 'AL', 'AP', 'AT', 'AX', 'BB', 'BF', 'BJ', 'BN', 'BR', 'BV', 'BZ', 'CD',
                            'CH', 'CL', 'CP', 'CT', 'CX', 'DB', 'DF', 'DJ', 'DN']
            row = 31
            index = 0
            stop = False
            for symbol in patronymic_receiving_side.upper():
                for col in range(index, len(list_columns)):
                    cell = list_columns[index] + str(row)
                    sheet[f'{cell}'] = symbol
                    index += 1
                    if col == 'DN':
                        stop = True
                    break
                if stop is True:
                    break

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="generation_arrival_notice.xlsx"'
    doc.save(response)
    return response