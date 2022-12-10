from fastapi import FastAPI

from app.analyzer.db import DBSetup
from app.analyzer.db.sertificate import FoundSertificate
from app.models.sertificate import SertificateInfo
from app.utils.exceptions_logger import catch_exceptions_middleware

app = FastAPI()
app.middleware("http")(catch_exceptions_middleware)


@app.on_event("startup")
async def startup():
    await DBSetup.init()


@app.post("/sertificate", status_code=201)
async def save_sertificate(info: SertificateInfo):
    sert = FoundSertificate(**info.dict())
    await sert.insert()
