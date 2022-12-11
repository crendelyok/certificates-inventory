from datetime import datetime
from ipaddress import IPv4Address

# pylint: disable=no-name-in-module
from pydantic import BaseModel, conlist


class CertificatesScanConfig(BaseModel):
    allowedProtocols: conlist(str, min_items=1)
    keyExchange: conlist(str, min_items=1)
    auth: conlist(str, min_items=1)
    macGen: conlist(str, min_items=1)
    ciphers: conlist(str, min_items=1)
    keyLengths: conlist(str, min_items=1)
    startDate: datetime
    endDate: datetime

    startAddr: IPv4Address
    endAddr: IPv4Address
    mask: int | IPv4Address | None


class SeachQueryId(BaseModel):
    query_id: int
