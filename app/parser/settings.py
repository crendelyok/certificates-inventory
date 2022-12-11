from functools import lru_cache
from os import cpu_count

from app.common.settings.base import BaseAppSettings


class Settings(BaseAppSettings):
    default_db_path: str

    workers_count: int = cpu_count()

    analyzer_port: int

    def get_analyzer_addr(self) -> str:
        return f"http://analyzer:{self.analyzer_port}"

    @staticmethod
    @lru_cache
    def get_settings():
        return Settings(**BaseAppSettings.get_yaml_config())
