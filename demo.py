import sys

from app.common.models.address import Address
from app.parser.scanners import SSLSocketScanner
from app.parser.certificate_getter import SSLCerificateGetter
from pprint import pprint
import threading
import socket
import time


def portscan(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.1)
    try:
        con = s.connect((ip, port))
        print('Port :', port, "is open.")
        con.close()
    except:
        # print('fuck')
        pass


# simply run python demo.py 8.8.8.8 443
if __name__ == "__main__":
    ip = sys.argv[1]
    port = sys.argv[2]
    domain = None
    if len(sys.argv) > 3:
        domain = sys.argv[3]

    # threads = []
    # port_number = 1
    # for x in range(1, 10000):
    #     t = threading.Thread(target=portscan, kwargs={'ip': ip, 'port': port_number})
    #     threads.append(t)
    #     port_number += 1
    #     t.start()
    # for x in threads:
    #     x.join()
    # print("all done")
    # time.sleep(30)
    addr = Address(ip, port, domain)
    cert_getter = SSLCerificateGetter()
    socketScanner = SSLSocketScanner([cert_getter], addr)
    socketScanner.scan()

    certificate = socketScanner.get_certificate()
    pprint(certificate.cerificate_data.dict())

