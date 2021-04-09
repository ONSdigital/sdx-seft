import json
import structlog

import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.exceptions import MaxRetryError
from requests.exceptions import ConnectionError
from app import DELIVER_SERVICE_URL
from app.errors import QuarantinableError, RetryableError

METADATA_FILE = 'metadata'
SEFT_FILE = 'seft'
UTF8 = "utf-8"

logger = structlog.get_logger()

session = requests.Session()
retries = Retry(total=5, backoff_factor=0.1)
session.mount('http://', HTTPAdapter(max_retries=retries))


def deliver_seft(meta_dict: dict, file_bytes: bytes):
    meta_bytes = json.dumps(meta_dict).encode()

    files = {
        METADATA_FILE: meta_bytes,
        SEFT_FILE: file_bytes}

    filename = meta_dict['filename']

    response = post(filename, files)
    status_code = response.status_code

    if status_code == 200:
        return True
    elif 400 <= status_code < 500:
        msg = "Bad Request response from sdx-deliver"
        logger.error(msg, status_code=status_code)
        raise RetryableError(msg)
    else:
        msg = "Bad response from sdx-deliver"
        logger.error(msg, status_code=status_code)
        raise QuarantinableError(msg)


def post(filename: str, files: dict):
    url = f"http://{DELIVER_SERVICE_URL}/deliver/seft"
    logger.info(f"Calling {url}")
    try:
        response = session.post(url, params={"filename": filename}, files=files)
    except MaxRetryError:
        logger.error("Max retries exceeded", request_url=url)
        raise RetryableError("Max retries exceeded")
    except ConnectionError:
        logger.error("Connection error", request_url=url)
        raise RetryableError("Connection error")

    return response
