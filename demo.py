from pprint import pprint
import sys

from app.common.models.address import Address
from app.parser.scanners import SSLSocketScanner
from app.parser.certificate_getter import SSLCerificateGetter


# simply run python demo.py 8.8.8.8 443
if __name__ == "__main__":
    ip = sys.argv[1]
    port = sys.argv[2]

    addr = Address(ip, port)
    cert_getter = SSLCerificateGetter()
    socketScanner = SSLSocketScanner([cert_getter], addr)
    assert socketScanner.scan()

    certificate = socketScanner.get_certificate()
    pprint(certificate.cerificate_data.dict())
