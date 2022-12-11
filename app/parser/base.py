from abc import ABC, abstractmethod
from ipaddress import IPv4Address
from typing import Iterable

from app.common.models.address import Address, IPRange
from app.parser.cerificate import Certificate


class BaseCertificateGetter(ABC):
    """
    Checks if certificate can be obtained and get it if possible
    """
    @abstractmethod
    def get(self, addr: Address, **kwargs) -> Certificate | None:
        pass


class BaseSocketScanner:
    def __init__(
        self,
        checkers: Iterable[BaseCertificateGetter],
        addr: Address,
    ):
        self._checkers = checkers
        self._addr = addr
        self._certificate: Certificate | None = None

    def get_certificate(self):
        return self._certificate

    def scan(self) -> bool:
        # only ssl
        for checker in self._checkers:
            cert = checker.get(self._addr)
            if cert:
                self._certificate = cert
                return True
        return False


class BaseIPScanner(ABC):
    def __init__(self, ip_range: IPRange):
        self._ip_range = ip_range

    @abstractmethod
    def ports(self, ip_address: IPv4Address) -> list[int]:
        pass

    @abstractmethod
    def scan(self):
        pass
