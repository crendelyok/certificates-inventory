import logging
import logging.config

from fastapi import FastAPI

from app.analyzer.db import DBSetup
from app.analyzer.db.certificate import FoundCertificate
from app.common.models.certificate import CertificateInfo
from app.common.utils.exceptions_logger import catch_exceptions_middleware
from app.common.utils.logger_config import get_logger_config

app = FastAPI(title="Analyzer")
app.middleware("http")(catch_exceptions_middleware)


@app.on_event("startup")
async def startup():
    await DBSetup.init()
    logging.config.dictConfig(get_logger_config())
    logging.info("Server %s has started", app.title)


@app.post("/certificate", status_code=201)
async def save_certificate(info: CertificateInfo):
    cert = FoundCertificate(**info.dict())
    await cert.insert()
