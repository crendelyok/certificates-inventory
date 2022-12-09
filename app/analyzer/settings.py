from functools import lru_cache

from app.settings.base import BaseAppSettings


class Settings(BaseAppSettings):
    default_db_path: str

    @staticmethod
    @lru_cache
    def get_settings():
        return Settings()
