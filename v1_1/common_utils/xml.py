import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import xml.dom.minidom as minidom
import math
from ..models.worker import DocumentsWorker

def json_to_xml(workers: list) -> str:
    root = ET.Element("root")

    table = ET.SubElement(root, 'Table')

    # --- Заполнение заголовков таблицы ----
    row0 = ET.SubElement(table, 'Row', attrib={'Index': '0'})
    cell1 = ET.SubElement(row0, 'Name', attrib={'Index': '0'})
    cell1.text = 'Имя'
    cell2 = ET.SubElement(row0, 'Surname', attrib={'Index': '1'})
    cell2.text = 'Фамилия'
    cell3 = ET.SubElement(row0, 'Patronymic', attrib={'Index': '2'})
    cell3.text = 'Отчество'

    cell4 = ET.SubElement(row0, 'Gender', attrib={'Index': '3'})
    cell4.text = 'Пол'

    cell5 = ET.SubElement(row0, 'Citizenship', attrib={'Index': '4'})
    cell5.text = 'Гражданство'

    cell6 = ET.SubElement(row0, 'Birthday', attrib={'Index': '5'})
    cell6.text = 'Дата рождения'

    cell7 = ET.SubElement(row0, 'PlaceBirth', attrib={'Index': '6'})
    cell7.text = 'Место рождения'

    cell8 = ET.SubElement(row0, 'Organization', attrib={'Index': '7'})
    cell8.text = 'Организация'

    cell9 = ET.SubElement(row0, 'Position', attrib={'Index': '8'})
    cell9.text = 'Должность'

    # Запись данных в таблицу
    for i in range(0, len(workers)):
        row_worker = ET.SubElement(table, 'Row',  attrib={'Index': f'{i + 1}'})

        cell_name = ET.SubElement(row_worker, 'CellName', attrib={'Index': '0'})
        cell_name.text = workers[i]['name']

        cell_surname = ET.SubElement(row_worker, 'CellSurname', attrib={'Index': '1'})
        cell_surname.text = workers[i]['surname']

        cell_patronymic = ET.SubElement(row_worker, 'CellPatronymic', attrib={'Index': '2'})
        cell_patronymic.text = workers[i]['patronymic']

        cell_gender = ET.SubElement(row_worker, 'CellGender', attrib={'Index': '3'})
        cell_gender.text = workers[i]['gender']

        cell_citizenship = ET.SubElement(row_worker, 'CellCitizenship', attrib={'Index': '4'})
        cell_citizenship.text = workers[i]['citizenship']

        cell_birthday = ET.SubElement(row_worker, 'CellBirthday', attrib={'Index': '5'})
        cell_birthday.text = workers[i]['birthday']

        cell_birthday = ET.SubElement(row_worker, 'CellPlaceBirth', attrib={'Index': '6'})
        cell_birthday.text = workers[i]['place_birth']

        cell_organization = ET.SubElement(row_worker, 'CellOrganization', attrib={'Index': '7'})
        cell_organization.text = workers[i]['organization']

        cell_position = ET.SubElement(row_worker, 'CellPosition', attrib={'Index': '8'})
        cell_position.text = workers[i]['position']

        cell_date_employment = ET.SubElement(row_worker, 'CellDateEmployment', attrib={'Index': '9'})
        cell_date_employment.text = workers[i]['date_employment']

        documents_worker = ET.SubElement(row_worker, 'Documents', attrib={'Index': '0'})

        documents = DocumentsWorker.objects.filter(worker_id=workers[i]['id'], archive=False)
        for doc in documents:
            if doc.type_document == 'passport':
                passport = ET.SubElement(documents_worker, 'Passport', attrib={'Index': '0'})

                series = ET.SubElement(passport, 'Series', attrib={'Index': '0'})
                series.text = doc.series

                number = ET.SubElement(passport, 'Number', attrib={'Index': '0'})
                number.text = doc.number

                issued_whom = ET.SubElement(passport, 'IssuedWhom', attrib={'Index': '0'})
                issued_whom.text = doc.issued_whom

                date_issue = str(doc.date_issue).split('-')
                date_issue = f'{date_issue[2]}.{date_issue[1]}.{date_issue[0]}'
                el_date_issue = ET.SubElement(passport, 'DateIssue', attrib={'Index': '0'})
                el_date_issue.text = date_issue

                date_end = str(doc.date_end).split('-')
                date_end = f'{date_end[2]}.{date_end[1]}.{date_end[0]}'
                el_date_end = ET.SubElement(passport, 'DateEnd', attrib={'Index': '0'})
                el_date_end.text = date_end
            elif doc.type_document == 'migration_card':
                migration_card = ET.SubElement(documents_worker, 'MigrationCard', attrib={'Index': '0'})

                series = ET.SubElement(migration_card, 'Series', attrib={'Index': '0'})
                series.text = doc.series

                number = ET.SubElement(migration_card, 'Number', attrib={'Index': '0'})
                number.text = doc.number

                date_issue = str(doc.date_issue).split('-')
                date_issue = f'{date_issue[2]}.{date_issue[1]}.{date_issue[0]}'
                el_date_issue = ET.SubElement(migration_card, 'DateIssue', attrib={'Index': '0'})
                el_date_issue.text = date_issue

                date_end = str(doc.date_end).split('-')
                date_end = f'{date_end[2]}.{date_end[1]}.{date_end[0]}'
                el_date_end = ET.SubElement(migration_card, 'DateEnd', attrib={'Index': '0'})
                el_date_end.text = date_end
            elif doc.type_document == 'registration':
                registration = ET.SubElement(documents_worker, 'Registration', attrib={'Index': '0'})

                date_issue = str(doc.date_issue).split('-')
                date_issue = f'{date_issue[2]}.{date_issue[1]}.{date_issue[0]}'
                el_date_issue = ET.SubElement(registration, 'DateIssue', attrib={'Index': '0'})
                el_date_issue.text = date_issue

                date_end = str(doc.date_end).split('-')
                date_end = f'{date_end[2]}.{date_end[1]}.{date_end[0]}'
                el_date_end = ET.SubElement(registration, 'DateEnd', attrib={'Index': '0'})
                el_date_end.text = date_end
            elif doc.type_document == 'patent':
                patent = ET.SubElement(documents_worker, 'Patent', attrib={'Index': '0'})

                series = ET.SubElement(patent, 'Series', attrib={'Index': '0'})
                series.text = doc.series

                number = ET.SubElement(patent, 'Number', attrib={'Index': '0'})
                number.text = doc.number

                issued_whom = ET.SubElement(patent, 'IssuedWhom', attrib={'Index': '0'})
                issued_whom.text = doc.issued_whom

                territory_action = ET.SubElement(patent, 'TerritoryAction')
                territory_action.text = doc.territory_action

                date_issue = str(doc.date_issue).split('-')
                date_issue = f'{date_issue[2]}.{date_issue[1]}.{date_issue[0]}'
                el_date_issue = ET.SubElement(patent, 'DateIssue', attrib={'Index': '0'})
                el_date_issue.text = date_issue

                date_end = str(doc.date_end).split('-')
                date_end = f'{date_end[2]}.{date_end[1]}.{date_end[0]}'
                el_date_end = ET.SubElement(patent, 'DateEnd', attrib={'Index': '0'})
                el_date_end.text = date_end
            elif doc.type_document == 'paycheck':
                paycheck = ET.SubElement(documents_worker, 'Paycheck', attrib={'Index': '0'})

                date_end = str(doc.date_end).split('-')
                date_end = f'{date_end[2]}.{date_end[1]}.{date_end[0]}'
                el_date_end = ET.SubElement(paycheck, 'DateEnd', attrib={'Index': '0'})
                el_date_end.text = date_end
            elif doc.type_document == 'temporary_residence':
                temporary_residence = ET.SubElement(documents_worker, 'TemporaryResidence', attrib={'Index': '0'})

                series = ET.SubElement(temporary_residence, 'Series', attrib={'Index': '0'})
                series.text = doc.series

                number = ET.SubElement(temporary_residence, 'Number', attrib={'Index': '0'})
                number.text = doc.number

                issued_whom = ET.SubElement(temporary_residence, 'IssuedWhom', attrib={'Index': '0'})
                issued_whom.text = doc.issued_whom

                date_issue = str(doc.date_issue).split('-')
                date_issue = f'{date_issue[2]}.{date_issue[1]}.{date_issue[0]}'
                el_date_issue = ET.SubElement(temporary_residence, 'DateIssue', attrib={'Index': '0'})
                el_date_issue.text = date_issue

                date_end = str(doc.date_end).split('-')
                date_end = f'{date_end[2]}.{date_end[1]}.{date_end[0]}'
                el_date_end = ET.SubElement(temporary_residence, 'DateEnd', attrib={'Index': '0'})
                el_date_end.text = date_end
            elif doc.type_document == 'residence_permit':
                residence_permit = ET.SubElement(documents_worker, 'ResidencePermit', attrib={'Index': '0'})

                series = ET.SubElement(residence_permit, 'Series', attrib={'Index': '0'})
                series.text = doc.series

                number = ET.SubElement(residence_permit, 'Number', attrib={'Index': '0'})
                number.text = doc.number

                issued_whom = ET.SubElement(residence_permit, 'IssuedWhom', attrib={'Index': '0'})
                issued_whom.text = doc.issued_whom

                date_issue = str(doc.date_issue).split('-')
                date_issue = f'{date_issue[2]}.{date_issue[1]}.{date_issue[0]}'
                el_date_issue = ET.SubElement(residence_permit, 'DateIssue', attrib={'Index': '0'})
                el_date_issue.text = date_issue

                date_end = str(doc.date_end).split('-')
                date_end = f'{date_end[2]}.{date_end[1]}.{date_end[0]}'
                el_date_end = ET.SubElement(residence_permit, 'DateEnd', attrib={'Index': '0'})
                el_date_end.text = date_end
            elif doc.type_document == 'certificate_asylum':
                certificate_asylum = ET.SubElement(documents_worker, 'CertificateAsylum', attrib={'Index': '0'})

                series = ET.SubElement(certificate_asylum, 'Series', attrib={'Index': '0'})
                series.text = doc.series

                number = ET.SubElement(certificate_asylum, 'Number', attrib={'Index': '0'})
                number.text = doc.number

                issued_whom = ET.SubElement(certificate_asylum, 'IssuedWhom', attrib={'Index': '0'})
                issued_whom.text = doc.issued_whom

                date_issue = str(doc.date_issue).split('-')
                date_issue = f'{date_issue[2]}.{date_issue[1]}.{date_issue[0]}'
                el_date_issue = ET.SubElement(certificate_asylum, 'DateIssue', attrib={'Index': '0'})
                el_date_issue.text = date_issue

                date_end = str(doc.date_end).split('-')
                date_end = f'{date_end[2]}.{date_end[1]}.{date_end[0]}'
                el_date_end = ET.SubElement(certificate_asylum, 'DateEnd', attrib={'Index': '0'})
                el_date_end.text = date_end
            elif doc.type_document == 'SNILS':
                SNILS = ET.SubElement(documents_worker, 'SNILS', attrib={'Index': '0'})

                number = ET.SubElement(SNILS, 'Number', attrib={'Index': '0'})
                number.text = doc.number
            elif doc.type_document == 'INN':
                INN = ET.SubElement(documents_worker, 'INN', attrib={'Index': '0'})

                number = ET.SubElement(INN, 'Number', attrib={'Index': '0'})
                number.text = doc.number

    xml_string = minidom.parseString(ET.tostring(root)).toprettyxml(indent='  ', newl='\n')
    return xml_string