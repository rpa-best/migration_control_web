from dadata import Dadata

def OrganizationSearch(value):
    token = 'de4144a486735962685109c249279deb926a1331'
    dadata = Dadata(token)
    return dadata.find_by_id('party', value)