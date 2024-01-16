from dadata import Dadata


token = 'de4144a486735962685109c249279deb926a1331'
dadata = Dadata(token)
bankInfo = dadata.find_by_id('party', '7804525530')
print(bankInfo)