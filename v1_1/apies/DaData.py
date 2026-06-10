import os
import re

from dadata import Dadata

dadata = Dadata(os.getenv('DADATA_TOKEN'))


def OrganizationSearch(value):
    return dadata.find_by_id('party', value)


def AddressSearch(value):
    try:
        return dadata.suggest('address', value)[0]['unrestricted_value']
    except Exception:
        return None


def GetCity(value):
    city_regex = r'(?:г\.?\s*|гор\s*од?)([\w\s-]+?),'
    city_match = re.search(city_regex, value)

    if city_match:
        city_name = city_match.group(1)
        return city_name
    else:
        try:
            if len(dadata.suggest('address', value)[0]['data']['city']) != 0:
                return dadata.suggest('address', value)[0]['data']['city']
            else:
                return ''
        except Exception:
            return ''


def GetInfoBank(bank_id):
    return dadata.find_by_id('bank', bank_id)
