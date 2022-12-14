from functools import lru_cache

from app.common.settings.base import BaseAppSettings


class Settings(BaseAppSettings):
    parser_port: int
    analyzer_port: int

    def get_parser_addr(self) -> str:
        return f"http://parser:{self.parser_port}"

    def get_analyzer_addr(self) -> str:
        return f"http://analyzer:{self.analyzer_port}"

    @staticmethod
    @lru_cache
    def get_settings():
        return Settings(**BaseAppSettings.get_yaml_config())
