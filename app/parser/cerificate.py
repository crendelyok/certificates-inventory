import cryptography
import tempfile
import ssl

from app.parser.base import Address
from app.parser.constants import CERTIFICATE_PUBLIC_KEY_TYPES


class Certificate():
    def __init__(self, bcert, addr: Address):
        """
        bcert is der_x509 binary formatted certificate
        """

        self.cerificate_data = {
            "ca": None,
            "notAfter": None,
            "notBefore": None,
            "PublicKeyLen": None,
            "PublicKeyAlg": None,
            "SignatureAlg": None,
        }

        # get info from cert dict
        try:
            with tempfile.TemporaryFile() as f:
                f.write(ssl.DER_cert_to_PEM_cert(bcert))
                cert_dict = ssl._ssl._test_decode_cert(f.name)
                self.cerificate_data["ca"] = cert_dict["issuer"]
                self.cerificate_data["notAfter"] = cert_dict["notAfter"]
                self.cerificate_data["notBefore"] = cert_dict["notBefore"]
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
        except:
            pass

    @staticmethod
    def get_public_key_alg(public_key):
        return public_key.__class__.__name__

    @staticmethod
    def get_signature_alg(public_key):
        return public_key.__class__.__name__
