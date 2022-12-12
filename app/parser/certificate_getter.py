import logging
import socket
import ssl

from app.common.models.address import Address
from app.parser.base import BaseCertificateGetter
from app.parser.cerificate import Certificate
from app.parser import SOCKET_CONN_TTL

logging.getLogger(__name__)


class BinCertException(Exception):
    pass


class SSLCerificateGetter(BaseCertificateGetter):
    def __init__(self, query_id: int | None = None):
        self._query_id = query_id
        super().__init__()

    def get(self, addr: Address, **kwargs) -> Certificate | None:
        # get binary certificate and decode
        try:
            bcert = self._create_binary_certificate(addr)
        except Exception as exc:
            logging.warning("SSLCerificateGetter: Can't create binary certificate: %s", str(exc))
            return None

        # check if it's self-signed
        params = {"issuerError": True}
        try:
            params["issuerError"] = self.check_issuer_error(addr)
        except Exception as exc:
            logging.warning(exc)
        return Certificate(bcert, addr, query_id=self._query_id, params=params)

    @staticmethod
    def check_issuer_error(addr: Address) -> bool:
        # create socket
        try:
            hostname = addr.ip_addr if addr.domain_name is None else addr.domain_name
            myctx = ssl.create_default_context()
            myctx.check_hostname = False
            myctx.verify_mode = ssl.CERT_REQUIRED
            myctx.verify_flags = ssl.VERIFY_X509_STRICT
            socket_conn = myctx.wrap_socket(socket.socket(), server_hostname=hostname)
            socket_conn.connect(addr.as_pair())
        except Exception as exc:
            logging.warning(exc)
            return True
        return False

    @staticmethod
    def _create_binary_certificate(addr: Address):
        # create socket
        try:
            hostname = addr.ip_addr if addr.domain_name is None else addr.domain_name
            myctx = ssl.create_default_context()
            myctx.check_hostname = False
            myctx.verify_mode = ssl.CERT_NONE
            socket_conn = myctx.wrap_socket(socket.socket(), server_hostname=hostname)
            socket_conn.settimeout(SOCKET_CONN_TTL)
            socket_conn.connect(addr.as_pair())
            binary_cert = socket_conn.getpeercert(binary_form=True)
        except ValueError as vexc:
            raise BinCertException("Can't establish connection") from vexc
        except TimeoutError as exc:
            logging.warning(exc)
            raise BinCertException("Timeout socket error") from exc
        except Exception as exc:
            logging.warning(exc)
            raise BinCertException("Can't get certificate") from exc

        return binary_cert
