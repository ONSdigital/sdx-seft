import json
import time

import structlog
import requests
import google.auth.transport.requests
import google.oauth2.id_token

from app import DELIVER_SERVICE_URL, CONFIG
from app.errors import QuarantinableError, RetryableError

METADATA_FILE = 'metadata'
FILE_NAME = 'filename'
SEFT_FILE = 'seft'
UTF8 = "utf-8"

logger = structlog.get_logger()


def deliver_seft(meta_dict: dict, file_bytes: bytes):
    """
    delivers a seft  submission. Returns True or raises appropriate error on response.
    """
    meta_bytes = json.dumps(meta_dict).encode()

    files = {
        METADATA_FILE: meta_bytes,
        SEFT_FILE: file_bytes}

    filename = meta_dict['filename']

    trying = True
    retries = 0
    max_retries = 3
    http_response = None
    while trying:
        try:
            http_response = post(filename, files)
            trying = False
        except RetryableError:
            retries += 1
            if retries > max_retries:
                trying = False
            else:
                # sleep for 20 seconds
                time.sleep(20)
                logger.info("trying again...")

    if http_response:
        status_code = http_response.status_code
        if status_code == 200:
            return True
        elif 400 <= status_code < 500:
            msg = f"Bad Request response from sdx-deliver: {http_response.reason}"
            logger.error(msg, status_code=status_code)
            raise QuarantinableError(msg)
        else:
            msg = f"Bad Request response from sdx-deliver: {http_response.reason}"
            logger.error(msg, status_code=status_code)
            raise RetryableError(msg)
    else:
        msg = f"No response from sdx-deliver!"
        logger.error(msg)
        raise RetryableError(msg)


def post(filename: str, files: dict):
    """
    Constructs the http call to the seft deliver service endpoint and posts the request.
    """

    audience = CONFIG.DELIVER_SERVICE_URL
    endpoint = f"{audience}/deliver/seft"
    auth_req = google.auth.transport.requests.Request()
    id_token = google.oauth2.id_token.fetch_id_token(auth_req, audience)
    logger.info(f"Calling {endpoint}")

    try:
        response = requests.post(
            endpoint,
            params={FILE_NAME: filename},
            files=files,
            headers={"Authorization": f"Bearer {id_token}"}
        )

    except ConnectionError:
        logger.error("Connection error", request_url=endpoint)
        raise RetryableError("Connection error")

    return response
