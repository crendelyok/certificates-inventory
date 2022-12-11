from datetime import datetime
import logging
import logging.config

from fastapi import FastAPI

from app.common.models.address import IPRange
from app.common.models.config import CertificatesScanConfig, SeachQueryId
from app.common.database.search_query import SearchQuery
from app.common.database.db_setup import DBSetup
from app.common.utils.exceptions_logger import catch_exceptions_middleware
from app.common.utils.logger_config import get_logger_config
from app.common.utils.network import SingleSession, SyncSingleSession
from app.parser.ip_scanner import IPScanner
from app.parser.settings import Settings
from app.parser.worker import ScannerQueue


app = FastAPI(title="Parser")
app.middleware("http")(catch_exceptions_middleware)


@app.on_event("startup")
async def startup():
    await DBSetup.init(Settings.get_settings().default_db_path)
    logging.config.dictConfig(get_logger_config())
    await SingleSession.init()
    SyncSingleSession.init()
    ScannerQueue.init()
    logging.info("Server %s has started", app.title)


@app.on_event("shutdown")
async def shutdown():
    await SingleSession.close()
    SyncSingleSession.close()


@app.post("/scan")
async def start_scan(config: CertificatesScanConfig):
    config_dict = config.to_json()
    time_created = datetime.now()
    query = SearchQuery(config=config_dict, time_created=time_created)
    query_id = await query.insert()

    ip_range = IPRange(
        start=config.startAddr,
        end=config.endAddr,
        mask=config.mask
    )
    try:
        ScannerQueue.get_instance().put_nowait(IPScanner(ip_range, query_id))
    except Exception as exc:
        logging.critical(exc, exc_info=True)

    resp = await SingleSession.request(
        "POST",
        f"{Settings.get_settings().get_analyzer_addr()}/user_params",
        json={"config": config_dict, "query_id": query_id, "time_created": str(time_created)}
    )
    if not resp.ok:
        logging.error("Failed to send query config (query_id %d) to analyzer", query_id)

    return SeachQueryId(query_id=query_id).dict()
