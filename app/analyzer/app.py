import asyncio
from datetime import datetime, timedelta
import logging
import logging.config

from fastapi import FastAPI, HTTPException

from app.analyzer.db.certificate import FoundCertificate
from app.analyzer.settings import Settings
from app.common.database.search_query import SearchQuery
from app.common.models.certificate import CertificateInfo
from app.common.models.config import SearchQueryInfo
from app.common.database.db_setup import DBSetup
from app.common.utils.exceptions_logger import catch_exceptions_middleware
from app.common.utils.logger_config import get_logger_config


def prepare_cert_to_db(data: CertificateInfo):
    return FoundCertificate(
        certificate=data.bcert,
        query_id=data.queryId,
        ip_addr=data.ip,
        port=data.port,
        start_time=data.notBefore,
        expiry_time=data.notAfter,
        keylen=data.PublicKeyLen,
        algo_signature=data.SignatureAlg,
        algo_cipher=data.HashAlg,
    )


def prepare_user_data_to_front(user: SearchQuery):
    return {
        "time_created": user.time_created,
        "config": user.config,
    }


def generate_output(cert: FoundCertificate, user_info: dict):
    output = {}
    output['ip'] = cert.ip_addr
    output['port'] = cert.port
    if datetime.now() > cert.expiry_time:
        output['is_expired'] = 'Yes'
    else:
        output['is_expired'] = 'No'
    if user_info['end_date'] - user_info['start_date'] < cert.expiry_time - cert.start_time:
        output['is_long_term'] = 'Yes'
    else:
        output['is_log_term'] = 'No'
    if user_info['keylen'] <= cert.keylen:
        output['is_keylen_safe'] = 'Yes'
    else:
        output['is_keylen_safe'] = 'No'
    if user_info['algo_signature'].find(cert.algo_signature) != -1:
        output['is_algo_signature_safe'] = 'Yes'
    else:
        output['is_algo_signature_safe'] = 'No'
    if user_info['algo_cipher'].find(cert.algo_cipher) != -1:
        output['is_algo_cipher_safe'] = 'Yes'
    else:
        output['is_algo_cipher_safe'] = 'No'
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
async def save_cert_info(cert_info : CertificateInfo):
    cert = prepare_cert_to_db(cert_info)
    await cert.insert()


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
    return [generate_output(cert, user_info_dict) for cert in cert_data_list]


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
        "ke_ecdhe": 1,
        "a_ecdhe": 1,
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
