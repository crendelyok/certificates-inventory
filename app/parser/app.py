import logging
import logging.config

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.common.models.config import CertificatesScanConfig
from app.common.utils.exceptions_logger import catch_exceptions_middleware
from app.common.utils.logger_config import get_logger_config


app = FastAPI(title="Parser")
app.middleware("http")(catch_exceptions_middleware)


@app.on_event("startup")
async def startup():
    logging.config.dictConfig(get_logger_config())
    logging.info("Server %s has started", app.title)


@app.post("/scan")
async def start_scan(config: CertificatesScanConfig):
    return JSONResponse({}, status_code=201)


@app.get("/scan", status_code=200)
async def get_scan_result(scan_id: int):
    pass
