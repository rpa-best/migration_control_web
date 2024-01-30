from dadata import Dadata

token = 'de4144a486735962685109c249279deb926a1331'
dadata = Dadata(token)

def OrganizationSearch(value):
    return dadata.find_by_id('party', value)


def AddressSearch(value):
    try:
        return dadata.suggest('address', value)[0]['unrestricted_value']
    except ValueError:
        return None
