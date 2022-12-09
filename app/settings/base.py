from enum import Enum

# pylint: disable=no-name-in-module
from pydantic import BaseModel


class AppType(Enum, str):
    DEV = "dev"
    PROD = "prod"


class BaseAppSettings(BaseModel):
    app_type: AppType = AppType.DEV
