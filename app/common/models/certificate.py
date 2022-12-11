from datetime import datetime
from ipaddress import IPv4Address
from typing import Any

# pylint: disable=no-name-in-module
from pydantic import BaseModel


class OpenKeyCertificate(BaseModel):
    key: bytes
    expires_at: datetime
    emitter_name: str
    owner_name: str
    sign: bytes


class CertificateInfo(BaseModel):
    bcert: bytes
    issuer: Any
    notAfter: datetime
    notBefore: datetime
    PublicKeyLen: int
    PublicKeyAlg: str
    SignatureAlg: str
    HashAlg: str
    issuerError: bool

    ip: IPv4Address
    port: int

    queryId: int | None

    def to_json(self):
        res = self.dict()
        for name in (
            "notAfter",
            "notBefore",
            "ip",
        ):
            res[name] = str(res[name])
        return res
