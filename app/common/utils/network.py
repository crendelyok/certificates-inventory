from ipaddress import IPv4Address
import socket
from typing import Iterable

from requests import Response, Session
from requests.adapters import HTTPAdapter, Retry

from aiohttp import ClientResponse, ClientSession, ClientTimeout
from yarl import URL


class SingleSession:
    _session: ClientSession | None = None

    @classmethod
    async def init(cls, **kwargs):
        if "timeout" not in kwargs:
            kwargs["timeout"] = ClientTimeout(total=10)
        cls._session = ClientSession(**kwargs)

    @classmethod
    async def close(cls):
        await cls._session.close()

    @classmethod
    async def request(cls, method: str, url: str | URL, **kwargs) -> ClientResponse:
        return await cls._session.request(method, url, **kwargs)


class SyncSingleSession:
    _session: Session | None = None

    @classmethod
    def init(
        cls,
        backoff_factor: float = 0.3,
        max_retries: int = 6,
        status_forcelist: Iterable[int] = (429, 500, 502, 503, 504,)
    ):
        cls._session = Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        cls._session.mount("http://", adapter)
        cls._session.mount("https://", adapter)

    @classmethod
    def close(cls):
        cls._session.close()

    @classmethod
    def request(cls, method: str, url: str | URL, **kwargs) -> Response:
        return cls._session.request(method, url, **kwargs)


def ip_available(ip_address: str | IPv4Address) -> bool:
    if isinstance(ip_address, IPv4Address):
        ip_address = str(ip_address)
    try:
        socket.gethostbyaddr(ip_address)
        return True
    except socket.herror:
        return False
