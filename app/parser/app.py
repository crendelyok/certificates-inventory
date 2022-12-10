from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.models.config import SertificatesScanConfig
from app.utils.exceptions_logger import catch_exceptions_middleware


app = FastAPI()
app.middleware("http")(catch_exceptions_middleware)


@app.post("/scan")
async def start_scan(config: SertificatesScanConfig):
    return JSONResponse({}, status_code=201)


@app.get("/scan", status_code=200)
async def get_scan_result(scan_id: int):
    pass
