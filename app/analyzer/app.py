import asyncio
from datetime import datetime, timedelta
import logging
import logging.config

from fastapi import FastAPI, HTTPException

from app.analyzer.db.certificate import FoundCertificate
from app.analyzer.settings import Settings
from app.common.database.search_query import SearchQuery
from app.common.models.certificate import CertificateInfo
from app.common.models.config import CertificatesScanConfig, SearchQueryInfo
from app.common.database.db_setup import DBSetup
from app.common.utils.exceptions_logger import catch_exceptions_middleware
from app.common.utils.logger_config import get_logger_config


def prepare_cert_to_db(data: CertificateInfo):
    return FoundCertificate(**data.to_json(convert_datetime=False))


def prepare_user_data_to_front(user: SearchQuery) -> dict:
    return SearchQueryInfo(
        config=user.config,
        query_id=user.rowid,
        time_created=user.time_created
    ).dict()


def yes_no_predicate(pred: bool) -> str:
    return 'Yes' if pred else 'No'


def generate_output(cert: FoundCertificate, user_config: CertificatesScanConfig):
    output = {
        'cert': cert.to_json(),
        'is_version_safe': yes_no_predicate(cert.version in user_config.allowedProtocols),
        'is_expired': yes_no_predicate(datetime.now() > cert.notAfter),
        'is_long_term': yes_no_predicate(user_config.endDate - user_config.startDate <\
                                         cert.notAfter - cert.notBefore),
        'is_keylen_safe': yes_no_predicate(any(x <= cert.PublicKeyLen for x in user_config.keyLengths)),
        'is_public_key_safe': yes_no_predicate(cert.PublicKeyAlg in user_config.keyExchange),
        'is_algo_signature_safe': yes_no_predicate(cert.SignatureAlg in user_config.keyExchange),
        'is_algo_cipher_safe': yes_no_predicate(cert.HashAlg in user_config.macGen),
        'is_issuer_error': yes_no_predicate(cert.issuerError),
    }
    return output


app = FastAPI(title="Analyzer")
app.middleware("http")(catch_exceptions_middleware)


@app.on_event("startup")
async def startup():
    await DBSetup.init(Settings.get_settings().default_db_path)
    logging.config.dictConfig(get_logger_config())
    logging.info("Server %s has started", app.title)


# send user params by id to front
@app.get("/user_params", status_code = 200)
async def get_user_params(user_id : int):
    user_data = await SearchQuery.get_by_id(user_id)
    return prepare_user_data_to_front(user_data)


# wait for user params
# post them to db
@app.post("/user_params", status_code = 201)
async def define_user_params(user_info: SearchQueryInfo):
    user = SearchQuery(
        rowid=user_info.query_id,
        config=user_info.config.to_json(),
        time_created=user_info.time_created,
    )
    await user.insert()


# wait for cert info from parser
# post that to db
@app.post("/raw_cert", status_code = 201)
async def save_cert_info(cert_info: CertificateInfo):
    try:
        cert = prepare_cert_to_db(cert_info)
        await cert.insert()
    except Exception as exc:
        logging.critical(exc, exc_info=True)


# send analyzed info by id to front
@app.get("/reports", status_code = 200)
async def get_by_id(query_id : int):
    cert_data_list, user_data = await asyncio.gather(*[
        FoundCertificate.get_by_query_id(query_id),
        SearchQuery.get_by_id(query_id)
    ])
    if not user_data:
        raise HTTPException(status_code=404)

    user_info_dict = prepare_user_data_to_front(user_data)
    user_config = CertificatesScanConfig.parse_obj(user_info_dict["config"])
    return {
        "reports": [
            generate_output(cert, user_config)
            for cert in cert_data_list
        ],
        "config": user_info_dict["config"]
    }


@app.get("/history", status_code=200)
async def get_searches_history():
    return [prepare_user_data_to_front(user) for user in await SearchQuery.get_all()]


@app.get("/default_config", status_code=200)
async def get_default_config():
    now = datetime.now()
    start_date = now - timedelta(days=30)
    end_date = now + timedelta(days=120)
    time_format = Settings.get_settings().time_format
    return {
        "ap_tls1.3": 1,
        "ke_ecdh": 1,
        "ke_ed25519": 1,
        "ke_x25519": 1,
        "mg_sha256": 1,
        "mg_sha384": 1,
        "c_aes_gcm": 1,
        "c_aes_ccm": 1,
        "c_aes_cbc": 1,
        "kl_length128": 1,
        "kl_length256": 1,
        "startDate": datetime.strftime(start_date, time_format),
        "endDate": datetime.strftime(end_date, time_format),
    }
