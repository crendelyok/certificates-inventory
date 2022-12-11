import socket
import ssl

from app.parser import Address
from app.parser.base import BaseCertificateGetter
from app.parser.cerificate import Certificate


class SSLCerificateGetter(BaseCertificateGetter):
    async def get(self, addr: Address, **kwargs) -> Certificate | None:
        # get binary certificate and decode
        try:
            bcert = self.create_binary_certificate(addr)
        except Exception as e:
            print(e)
            return None
        return Certificate(bcert, addr)

    @staticmethod
    def create_binary_certificate(addr: Address):
        ip = addr.ip_addr
        port = int(addr.port)
        # create socket
        try:
            myctx = ssl.create_default_context()
            myctx.check_hostname = False
            myctx.verify_mode = ssl.CERT_NONE
            socket_conn = myctx.wrap_socket(socket.socket(), server_hostname=ip)
            socket_conn.connect((ip, port))
            binary_cert = socket_conn.getpeercert(binary_form=True)
        except ValueError:
            raise Exception("Can't establish connection")
        except Exception as e:
            print(e)
            raise Exception("Can't get certificate")

        return binary_cert
