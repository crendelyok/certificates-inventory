import logging

import cryptography.x509
import cryptography.hazmat.backends.openssl

from app.common.models.address import Address
from app.common.models.certificate import CertificateInfo

logging.getLogger(__name__)


class Certificate:
    def __init__(self, bcert,
                 addr: Address,
                 query_id: int | None = None,
                 params: dict | None = None):
        """
        bcert is der_x509 binary formatted certificate
        """
        # get info from binary itself
        try:
            cert = cryptography.x509.load_der_x509_certificate(
                bcert,
                cryptography.hazmat.backends.openssl.backend
            )
            self.cerificate_data = CertificateInfo(
                bcert=bcert,
                issuer=cert.issuer,
                notAfter=cert.not_valid_after,
                notBefore=cert.not_valid_before,
                PublicKeyLen=cert.public_key().key_size,
                PublicKeyAlg=self.get_public_key_alg(cert.public_key()),
                SignatureAlg=self.get_signature_alg(cert.public_key()),
                HashAlg=cert.signature_hash_algorithm.name,
                issuerError=False,
                ip=addr.ip_addr,
                port=addr.port,
                queryId=query_id,
            )
            if params:
                if "issuerError" in params:
                    self.cerificate_data.issuerError = params["issuerError"]
        except Exception as exc:
            logging.warning(exc)

    @staticmethod
    def get_public_key_alg(public_key):
        return public_key.__class__.__name__

    @staticmethod
    def get_signature_alg(public_key):
        return public_key.__class__.__name__
