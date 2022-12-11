from collections import namedtuple
from ipaddress import IPv4Address

# pylint: disable=no-name-in-module
from pydantic import BaseModel, validator


__address_fields = ("ip_addr", "port", "domain_name",)
class Address(namedtuple(
    "Address",
    __address_fields,
    defaults=(None,) * len(__address_fields)
)):
    __slots__ = ()

    def as_pair(self) -> tuple[str, int]:
        return (self.ip_addr, int(self.port),)


class IPRange(BaseModel):
    start: IPv4Address
    end: IPv4Address
    mask: int | IPv4Address | None

    @classmethod
    @validator("end")
    def validate_end(cls, value, values):
        if "start" not in values or value < values["start"]:
            start = values.get("start", None)
            raise ValueError(
                "end address must be greater than start: "
                f"got start = {start} and end = {value}"
            )
        return value
