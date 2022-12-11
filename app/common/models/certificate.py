from datetime import datetime

# pylint: disable=no-name-in-module
from pydantic import BaseModel


class OpenKeyCertificate(BaseModel):
    key: bytes
    expires_at: datetime
    emitter_name: str
    owner_name: str
    sign: bytes


class CertificateInfo(BaseModel):
    certificate: bytes
    query_id: int
    ip_addr: str
    port: int
    time_issued: datetime
    time_found: datetime
    extra_args: dict
