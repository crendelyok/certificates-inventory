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
