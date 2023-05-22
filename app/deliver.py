import json

from sdx_gcp.app import get_logger

from app import CONFIG, sdx_app

METADATA_FILE = 'metadata'
FILE_NAME = 'filename'
SEFT_FILE = 'seft'
TX_ID = "tx_id"
UTF8 = "utf-8"

logger = get_logger()


def deliver_seft(meta_dict: dict[str, str], file_bytes: bytes):
    """
    Post a seft submission to sdx-deliver.
    """
    meta_bytes = json.dumps(meta_dict).encode()

    files = {
        METADATA_FILE: meta_bytes,
        SEFT_FILE: file_bytes}

    filename = meta_dict['filename']
    tx_id = meta_dict['tx_id']

    domain = CONFIG.DELIVER_SERVICE_URL
    endpoint = "deliver/seft"
    sdx_app.http_post(domain, endpoint, None, params={FILE_NAME: filename, TX_ID: tx_id}, files=files)
