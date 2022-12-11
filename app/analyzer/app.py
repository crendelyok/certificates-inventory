import asyncio
from datetime import datetime
import json
import logging.config

from fastapi import FastAPI

from app.analyzer.db import DBSetup
from app.analyzer.db.certificate import FoundCertificate
from app.analyzer.db.user import FoundUser
from app.common.utils.exceptions_logger import catch_exceptions_middleware
from app.common.utils.logger_config import get_logger_config


def prepare_cert_to_db(data : dict):
    return FoundCertificate(
        certificate=data['cert'],
        query_id=data['query_id'],
        ip_addr=data['ip'],
        port=data['port'],
        start_time=data['notBefore'],
        expiry_time=data['notAfter'],
        keylen=data['keylen'],
        algo_signature=data['algo_signature'],
        algo_cipher=data['algo_cipher'],
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
    await DBSetup.init()
    logging.config.dictConfig(get_logger_config())


# send user params by id to front
@app.get("/user_params", status_code = 201)
async def get_user_params(user_id : int):
    user_data = await FoundUser.get_by_id(user_id)
    user_info_dict = prepare_user_data_to_front(user_data)
    return json.dumps(user_info_dict)


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
async def save_cert_info(cert_info_json_str : str):
    cert_info_dict = json.loads(cert_info_json_str)
    cert = prepare_cert_to_db(cert_info_dict)
    await cert.insert()


# send analyzed info by id to front
@app.get("/by_reports", status_code = 201)
async def get_by_id(user_id : int):
    cert_data_list, user_data = await asyncio.gather(*[
        FoundCertificate.get_by_query_id(user_id),
        FoundUser.get_by_id(user_id)
    ])
    user_info_dict = prepare_user_data_to_front(user_data)
    data_to_front = []
    for cert in cert_data_list:
        data_to_front.append(generate_output(cert, user_info_dict))
    return json.dumps(data_to_front)
