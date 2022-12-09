from datetime import datetime

# pylint: disable=no-name-in-module
from pydantic import BaseModel


class OpenKeySertificate(BaseModel):
    key: bytes
    expires_at: datetime
    emitter_name: str
    owner_name: str
    sign: bytes


class SertificateInfo(BaseModel):
    sertificate: bytes
    query_id: int
    ip_addr: str
    port: int
    time_issued: datetime
    time_found: datetime
    extra_args: dict
