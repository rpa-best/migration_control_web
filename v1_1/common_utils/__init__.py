
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    #Если значение есть, то это означает, что запрос был перенаправлен через прокси-сервер, и его IP-адрес находится
    # в значении этого ключа
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        #Если ключа 'HTTP_X_FORWARDED_FOR' нет, это означает, что запрос был отправлен напрямую, и его IP-адрес
        # находится в значении ключа 'REMOTE_ADDR' в словаре request.META
        ip = request.META.get('REMOTE_ADDR')
    return ip