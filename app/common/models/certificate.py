from datetime import datetime
from ipaddress import IPv4Address

from cryptography.x509 import Name
# pylint: disable=no-name-in-module
from pydantic import BaseModel, validator


class CertificateInfo(BaseModel):
    bcert: bytes
    version: str
    issuer: str
    notAfter: datetime
    notBefore: datetime
    PublicKeyLen: int
    PublicKeyAlg: str
    SignatureAlg: str
    HashAlg: str
    issuerError: bool = False

    ip: IPv4Address
    port: int

    queryId: int | None

    def to_json(self, convert_datetime: bool = True):
        res = self.dict()
        res["bcert"] = str(self.bcert)
        res["ip"] = str(self.ip)
        if convert_datetime:
            res["notAfter"] = str(self.notAfter)
            res["notBefore"] = str(self.notBefore)
        return res

    @classmethod
    @validator("issuer", pre=True)
    def validate_issuer(cls, value, _):
        if not value or not isinstance(value, (str, Name,)):
            raise ValueError(f"'issuer' must be of type 'str' or 'Name', got type {type(value)}")
        if isinstance(value, Name):
            return value.rfc4514_string()
        return value
