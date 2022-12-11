import logging
import socket
import ssl

from app.common.models.address import Address
from app.parser.base import BaseCertificateGetter
from app.parser.cerificate import Certificate

logging.getLogger(__name__)


class SSLCerificateGetter(BaseCertificateGetter):
    def __init__(self, query_id: int | None = None):
        self._query_id = query_id
        super().__init__()

    def get(self, addr: Address, **kwargs) -> Certificate | None:
        # get binary certificate and decode
        try:
            bcert = self.create_binary_certificate(addr)
        except Exception as exc:
            logging.warning(exc)
            return None
        return Certificate(bcert, addr, query_id=self._query_id)

    @staticmethod
    def create_binary_certificate(addr: Address):
        # create socket
        try:
            myctx = ssl.create_default_context()
            myctx.check_hostname = False
            myctx.verify_mode = ssl.CERT_NONE
            socket_conn = myctx.wrap_socket(socket.socket(), server_hostname=addr.ip_addr)
            socket_conn.connect(addr.as_pair())
            binary_cert = socket_conn.getpeercert(binary_form=True)
        except ValueError as vexc:
            raise Exception("Can't establish connection") from vexc
        except Exception as exc:
            logging.warning(exc)
            raise Exception("Can't get certificate") from exc

        return binary_cert
