import logging
import os
import ssl
import time

import cryptography.x509
import cryptography.hazmat.backends.openssl

from app.parser import Address

logging.getLogger(__name__)


class Certificate:
    def __init__(self, bcert, addr: Address):
        """
        bcert is der_x509 binary formatted certificate
        """

        self.cerificate_data = {
            "bcert": bcert,
            "ca": None,
            "notAfter": None,
            "notBefore": None,
            "PublicKeyLen": None,
            "PublicKeyAlg": None,
            "SignatureAlg": None,
            "ip": addr.ip_addr,
            "port": addr.port,
            "queryId": None,
        }

        # get info from cert dict
        filename = f"{str(time.time())}_cert.pem"
        try:
            with open(filename, encoding="utf-8", mode="w") as fstream:
                cert = ssl.DER_cert_to_PEM_cert(bcert)
                fstream.write(cert)
                fstream.seek(0)
                cert_dict = ssl._ssl._test_decode_cert(filename)
                self.cerificate_data["ca"] = cert_dict["issuer"]
                self.cerificate_data["notAfter"] = cert_dict["notAfter"]
                self.cerificate_data["notBefore"] = cert_dict["notBefore"]
        except Exception as exc:
            logging.warning(exc)
        finally:
            try:
                os.unlink(filename)
            except:
                pass

        # get info from binary itself
        try:
            cert = cryptography.x509.load_der_x509_certificate(
                bcert,
                cryptography.hazmat.backends.openssl.backend
            )
            self.cerificate_data["PublicKeyLen"] = cert.public_key().key_size
            self.cerificate_data["SignatureAlg"] = self.get_signature_alg(cert.public_key())
            self.cerificate_data["PublicKeyAlg"] = self.get_public_key_alg(cert.public_key())
        except Exception as exc:
            logging.warning(exc)

    @staticmethod
    def get_public_key_alg(public_key):
        return public_key.__class__.__name__

    @staticmethod
    def get_signature_alg(public_key):
        return public_key.__class__.__name__
