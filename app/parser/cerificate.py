import os

import cryptography.x509
import cryptography.hazmat.backends.openssl
import time
import ssl

from app.parser import Address


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
        }

        # get info from cert dict
        filename = f"{str(time.time())}_cert.pem"
        try:
            with open(filename, "w") as f:
                cert = ssl.DER_cert_to_PEM_cert(bcert)
                f.write(cert)
                f.seek(0)
                cert_dict = ssl._ssl._test_decode_cert(filename)
                self.cerificate_data["ca"] = cert_dict["issuer"]
                self.cerificate_data["notAfter"] = cert_dict["notAfter"]
                self.cerificate_data["notBefore"] = cert_dict["notBefore"]
        except Exception as e:
            print(e)
            pass
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
        except Exception as e:
            print(e)
            pass

    @staticmethod
    def get_public_key_alg(public_key):
        return public_key.__class__.__name__

    @staticmethod
    def get_signature_alg(public_key):
        return public_key.__class__.__name__
