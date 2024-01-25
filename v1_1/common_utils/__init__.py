from datetime import datetime, timedelta
from scapy.layers.l2 import ARP, Ether
from scapy.sendrecv import srp


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


def check_duplicate_registrations(ip_address, user_agent):
    # Определить начальное и конечное время для проверки
    start_time = datetime.now() - timedelta(days=1)
    end_time = datetime.now()

    # Создать ARP-запрос для определения наличия других устройств с указанным IP-адресом и MAC-адресом
    arp = ARP(pdst=ip_address)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp
    result = srp(packet, timeout=3, verbose=0)[0]

    # Проверить каждый полученный ответ
    for _, received_packet in result:
        ip = received_packet[ARP].psrc
        mac = received_packet[ARP].hwsrc
        time = datetime.fromtimestamp(received_packet.time)

        # Проверить, что полученный IP и MAC совпадают с теми, которые переданы в функцию
        if ip == ip_address and mac == user_agent:
            # Проверить, что время отправки пакета находится в заданном интервале
            if start_time <= time <= end_time:
                return True

    return False