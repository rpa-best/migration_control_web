from dadata import Dadata
import re

token = 'de4144a486735962685109c249279deb926a1331'
dadata = Dadata(token)

def OrganizationSearch(value):
    return dadata.find_by_id('party', value)


def AddressSearch(value):
    try:
        return dadata.suggest('address', value)[0]['unrestricted_value']
    except ValueError:
        return None


def GetCity(value):
    city_regex = r"г(?:ород)?\s+(.+?),"
    city_match = re.search(city_regex, value)

    try:
        if len(dadata.suggest('address', value)[0]['data']['city']) != 0:
            try:
                return dadata.suggest('address', value)[0]['data']['city']
            except ValueError:
                return ''
        else:
            if city_match:
                city_name = city_match.group(1)
                return city_name
            else:
                return ''
    except ValueError:
        return ''