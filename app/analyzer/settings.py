from functools import lru_cache

from app.common.settings.base import BaseAppSettings


class Settings(BaseAppSettings):
    default_db_path: str

    time_format: str = "%Y-%m-%d"

    @staticmethod
    @lru_cache
    def get_settings():
        return Settings(**BaseAppSettings.get_yaml_config())
