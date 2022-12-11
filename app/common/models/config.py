import datetime
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
    startDate: datetime.date
    endDate: datetime.date

    startAddr: IPv4Address
    endAddr: IPv4Address
    mask: int | IPv4Address | None

    def to_json(self):
        res = self.dict()
        for name in (
            "startDate",
            "endDate",
            "startAddr",
            "endAddr",
        ):
            res[name] = str(res[name])
        if isinstance(self.mask, IPv4Address):
            res["mask"] = str(res["mask"])
        return res

    @staticmethod
    def list_type_fields_names() -> set[str]:
        return set([
            "allowedProtocols",
            "keyExchange",
            "auth",
            "macGen",
            "ciphers",
            "keyLengths",
        ])


class SeachQueryId(BaseModel):
    query_id: int


class SearchQueryInfo(BaseModel):
    config: CertificatesScanConfig
    query_id: int
    time_created: datetime.datetime
