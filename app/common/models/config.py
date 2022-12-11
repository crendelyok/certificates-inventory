# pylint: disable=no-name-in-module
from pydantic import BaseModel, conlist


class CertificatesScanConfig(BaseModel):
    included_protocols: conlist(str, min_items=1)


class ScanStartedResponse(BaseModel):
    query_id: int
