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

        documents_dict = {
            'passport': ('Passport', ['Series', 'Number', 'IssuedWhom', 'DateIssue', 'DateEnd']),
            'migration_card': ('MigrationCard', ['Series', 'Number', 'DateIssue', 'DateEnd']),
            'registration': ('Registration', ['DateIssue', 'DateEnd']),
            'patent': ('Patent', ['Series', 'Number', 'IssuedWhom', 'TerritoryAction', 'DateIssue', 'DateEnd']),
            'paycheck': ('Paycheck', ['DateEnd']),
            'temporary_residence': ('TemporaryResidence', ['Series', 'Number', 'IssuedWhom', 'DateIssue', 'DateEnd']),
            'residence_permit': ('ResidencePermit', ['Series', 'Number', 'IssuedWhom', 'DateIssue', 'DateEnd']),
            'certificate_asylum': ('CertificateAsylum', ['Series', 'Number', 'IssuedWhom', 'DateIssue', 'DateEnd']),
        }

        for doc in documents:
            document_type = doc.type_document
            if document_type in documents_dict:
                document_element = ET.SubElement(documents_worker, documents_dict[document_type][0],
                                                 attrib={'Index': '0'})
                for element_name in documents_dict[document_type][1]:
                    if element_name == 'DateIssue':
                        element_name = 'Date_Issue'
                    elif element_name == 'DateEnd':
                        element_name = 'Date_End'
                    elif element_name == 'IssuedWhom':
                        element_name = 'Issued_Whom'

                    element_value = getattr(doc, element_name.lower(), None)    # получение значения из документа

                    if element_value:
                        element = ET.SubElement(document_element, element_name.replace('_', ''
                                                                                       ), attrib={'Index': '0'})
                        if element_name.startswith('Date'):
                            element_value = str(element_value).split('-')
                            element_value = f'{element_value[2]}.{element_value[1]}.{element_value[0]}'
                        element.text = element_value

    xml_string = minidom.parseString(ET.tostring(root)).toprettyxml(indent='  ', newl='\n')
    return xml_string