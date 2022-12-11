import asyncio
from datetime import datetime, timedelta
import json
import logging
import logging.config

from fastapi import FastAPI, HTTPException

from app.analyzer.db.certificate import FoundCertificate
from app.analyzer.db.user import FoundUser
from app.analyzer.settings import Settings
from app.common.models.certificate import CertificateInfo
from app.common.utils.db_setup import DBSetup
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


def prepare_user_to_db(data : dict):
    return FoundUser(
        start_time=data['start_date'],
        expiry_time=data['end_date'],
        keylen=data['keylen'],
        algo_signature=data['algo_signature'],
        algo_cipher=data['algo_cipher'],
    )


def prepare_user_data_to_front(user: FoundUser):
    return {
        'start_date': user.start_time,
        'end_date': user.expiry_time,
        'keylen': user.keylen,
        'algo_signature': user.algo_signature,
        'algo_cipher': user.algo_cipher,
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
    user_data = await FoundUser.get_by_id(user_id)
    return prepare_user_data_to_front(user_data)


# wait for user params
# post them to db
@app.post("/user_params", status_code = 201)
async def define_user_params(user_info_json_str : str):
    user_info_dict = json.loads(user_info_json_str)
    user = prepare_user_to_db(user_info_dict)
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
        FoundUser.get_by_id(query_id)
    ])
    if not user_data:
        raise HTTPException(status_code=404)

    user_info_dict = prepare_user_data_to_front(user_data)
    return [generate_output(cert, user_info_dict) for cert in cert_data_list]


@app.get("/history", status_code=200)
async def get_searches_history():
    return [prepare_user_data_to_front(user) for user in await FoundUser.get_all()]


@app.get("/default_config", status_code=200)
async def get_default_config():
    now = datetime.now()
    start_date = now - timedelta(days=30)
    end_date = now + timedelta(days=120)
    time_format = Settings.get_settings().time_format
    return {
        "ap_tls1.3": True,
        "ke_ecdhe": True,
        "a_ecdhe": True,
        "mg_sha256": True,
        "mg_sha384": True,
        "c_aes_gcm": True,
        "c_aes_ccm": True,
        "c_aes_cbc": True,
        "kl_length128": True,
        "kl_length256": True,
        "startDate": datetime.strftime(start_date, time_format),
        "endDate": datetime.strftime(end_date, time_format),
    }
