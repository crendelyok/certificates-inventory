from abc import ABC, abstractmethod
from collections import namedtuple
from typing import Iterable


__address_fields = ("ip_addr", "port", "domain_name",)
class Address(namedtuple(
    "Address",
    __address_fields,
    defaults=(None,) * len(__address_fields)
)):
    __slots__ = ()


class BaseProtocolChecker(ABC):
    @abstractmethod
    async def check(self, addr: Address, **kwargs) -> str | None:
        pass


class BaseSocketScanner:
    def __init__(
        self,
        checkers: Iterable[BaseProtocolChecker],
        addr: Address | None = None,
        ip_addr: str | None = None,
        port: int | None = None,
    ):
        self._checkers = checkers
        if addr:
            self.addr = addr
        else:
            self.addr = Address(ip_addr, port)
        self._sertificate: str | None = None

    def get_sertificate(self):
        return self._sertificate

    async def scan(self) -> bool:
        for checker in self._checkers:
            sert = await checker.check(self.addr)
            if sert:
                self._sertificate = sert
                return True
        return False
