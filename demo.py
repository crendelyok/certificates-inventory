import sys

from app.common.models.address import Address
from app.parser.scanners import SSLSocketScanner
from app.parser.certificate_getter import SSLCerificateGetter
from pprint import pprint
import threading
import socket


def portscan(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.1)
    try:
        con = s.connect((ip, port))
        print('Port :', port, "is open.")
        con.close()
    except:
        pass


# simply run python demo.py 8.8.8.8 443
if __name__ == "__main__":
    ip = sys.argv[1]
    port = sys.argv[2]
    domain = None
    if len(sys.argv) > 3:
        domain = sys.argv[3]

    port_number = 1
    for x in range(1, 65000):
        t = threading.Thread(target=portscan, kwargs={'ip' : ip, 'port': port_number})
        port_number += 1
        t.start()

    addr = Address(ip, port, domain)
    cert_getter = SSLCerificateGetter()
    socketScanner = SSLSocketScanner([cert_getter], addr)
    socketScanner.scan()

    certificate = socketScanner.get_certificate()
    pprint(certificate.cerificate_data.dict())

