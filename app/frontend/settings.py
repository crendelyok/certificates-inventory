from functools import lru_cache
import socket
from typing import ClassVar

from fastapi.templating import Jinja2Templates

from app.settings.base import BaseAppSettings


class Settings(BaseAppSettings):
    templates: ClassVar[Jinja2Templates] = Jinja2Templates("web/templates")

    host_ip: ClassVar[str] = socket.gethostbyname(socket.gethostname())

    parser_port: int

    def get_parser_addr(self) -> str:
        return f"http://{self.host_ip}:{self.parser_port}"

    @staticmethod
    @lru_cache
    def get_settings():
        return Settings()
