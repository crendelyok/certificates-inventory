from enum import Enum

# pylint: disable=no-name-in-module
from pydantic import BaseSettings, Extra
import yaml


class AppType(str, Enum):
    DEV = "dev"
    PROD = "prod"


class BaseAppSettings(BaseSettings, extra=Extra.allow):
    app_type: AppType = AppType.DEV

    config_file: str = "config.yaml"

    @staticmethod
    def get_yaml_config() -> dict:
        with open(BaseAppSettings().config_file, encoding="utf-8", mode="r") as stream:
            return yaml.safe_load(stream)
