import logging
import logging.config

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
# pylint: disable=no-name-in-module
from pydantic import ValidationError
from starlette.datastructures import FormData
from starlette.staticfiles import StaticFiles

from app.common.models.config import CertificatesScanConfig, SeachQueryId
from app.common.utils.exceptions_logger import catch_exceptions_middleware
from app.common.utils.logger_config import get_logger_config
from app.common.utils.network import SingleSession
from app.frontend.settings import Settings

logging.getLogger(__name__)


app = FastAPI(title="Frontend")
app.middleware("http")(catch_exceptions_middleware)
app.mount("/static/", StaticFiles(directory="/app/frontend/web/static"), name="static")
app.templates = Jinja2Templates("/app/frontend/web/templates")


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
    return app.templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


@app.get("/searches_history", status_code=200)
async def get_search_history_page(request: Request):
    resp = await SingleSession.request(
        "GET",
        f"{Settings.get_settings().get_analyzer_addr()}/history"
    )
    if not resp.ok:
        raise HTTPException(status_code=resp.status)
    return app.templates.TemplateResponse(
        "searches_history.html",
        {"request": request, "history": await resp.json()}
    )


@app.get("/search_report/{query_id}", status_code=200)
async def get_search_reports_page(request: Request, query_id: int):
    resp = await SingleSession.request(
        "GET",
        f"{Settings.get_settings().get_analyzer_addr()}/reports",
        params={"query_id": query_id}
    )
    if not resp.ok:
        raise HTTPException(status_code=resp.status)

    resp_json: dict = await resp.json()
    return app.templates.TemplateResponse(
        "search_reports.html",
        {
            "request": request,
            "query_id": query_id,
            "reports": resp_json["reports"],
            "config": resp_json["config"],
        }
    )


@app.get("/search", status_code=200)
async def get_search_page(request: Request):
    resp = await SingleSession.request(
        "GET",
        f"{Settings.get_settings().get_analyzer_addr()}/default_config",
    )
    if not resp.ok:
        raise HTTPException(status_code=resp.status)
    return app.templates.TemplateResponse(
        "search.html",
        {"request": request, "check_map": await resp.json()}
    )


@app.post("/search", status_code=201)
async def start_search(request: Request):
    list_type_fields = CertificatesScanConfig.list_type_fields_names()
    req_form: FormData = await request.form()
    form_dict = {
        name: (req_form.getlist(name) if name in list_type_fields else req_form.getlist(name)[0])
        for name in req_form.keys()
    }
    try:
        config = CertificatesScanConfig.parse_obj(form_dict)
    except ValidationError as exc:
        logging.warning("Validation errors: %s", str(exc))
        return HTTPException(status_code=400, detail=str(exc))

    resp = await SingleSession.request(
        "POST",
        f"{Settings.get_settings().get_parser_addr()}/scan",
        json=config.to_json()
    )
    if not resp.ok:
        raise HTTPException(status_code=resp.status)
    try:
        resp_data = SeachQueryId(**(await resp.json()))
        return RedirectResponse(url=f"/search_report/{resp_data.query_id}", status_code=303)
    except ValidationError as exc:
        logging.warning("Failed search-start response: %s", str(exc))
        raise HTTPException(status_code=500) from exc
