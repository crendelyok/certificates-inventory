from abc import ABC, abstractmethod
from collections import namedtuple
from typing import Iterable

from app.parser.cerificate import Certificate


__address_fields = ("ip_addr", "port", "domain_name",)


class Address(namedtuple(
    "Address",
    __address_fields,
    defaults=(None,) * len(__address_fields)
)):
    __slots__ = ()


class BaseCertificateGetter(ABC):
    """
    Checks if certificate can be obtained and get it if possible
    """
    @abstractmethod
    async def get(self, addr: Address, **kwargs) -> Certificate | None:
        pass


class BaseSocketScanner:
    def __init__(
        self,
        checkers: Iterable[BaseCertificateGetter],
        addr: Address = None,
    ):
        self._checkers = checkers
        self._addr = addr
        self._certificate: Certificate | None = None

    def get_certificate(self):
        return self._certificate

    async def scan(self) -> bool:
        # only ssl
        for checker in self._checkers:
            cert = await checker.get(self._addr)
            if cert:
                self._certificate = sert
                return True
        return False
