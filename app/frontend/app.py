import logging
import logging.config

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
# pylint: disable=no-name-in-module
from pydantic import ValidationError
from starlette.staticfiles import StaticFiles

from app.common.utils.exceptions_logger import catch_exceptions_middleware
from app.common.utils.logger_config import get_logger_config
from app.common.utils.requests import SingleSession
from app.common.models.config import SertificatesScanConfig, ScanStartedResponse
from app.frontend.settings import Settings

logging.getLogger(__name__)


app = FastAPI(title="Frontend")
app.middleware("http")(catch_exceptions_middleware)
app.mount("/static/", StaticFiles(directory="/app/frontend/web/static"), name="static")


@app.on_event("startup")
async def startup():
    await SingleSession.init()
    logging.config.dictConfig(get_logger_config())
    logging.info("Server %s has started", app.title)


@app.on_event("shutdown")
async def shutdown():
    await SingleSession.close()


@app.get("/", status_code=200)
async def get_index_page(request: Request):
    return Settings.get_settings().templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


@app.get("/search_history", status_code=200)
async def get_search_history_page(request: Request):
    return Settings.get_settings().templates.TemplateResponse(
        "search_history.html",
        {"request": request}
    )


@app.get("/search", status_code=200)
async def get_search_page(request: Request):
    return Settings.get_settings().templates.TemplateResponse(
        "search.html",
        {"request": request}
    )


@app.post("/search", status_code=201)
async def start_search(config: SertificatesScanConfig):
    resp = await SingleSession.request(
        "POST",
        f"{Settings.get_settings().get_parser_addr()}/scan",
        json=config
    )
    try:
        resp_data = ScanStartedResponse(**(await resp.json()))
        return JSONResponse(resp_data.dict(), status_code=resp.status)
    except ValidationError as exc:
        logging.warning("Failed search-start response: %s", str(exc))
        raise HTTPException(status_code=500) from exc
