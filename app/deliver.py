import json
from typing import Final

from sdx_gcp.app import get_logger

from app import CONFIG, sdx_app
from app.definitions import Metadata

METADATA_FILE: Final[str] = 'metadata'
FILE_NAME: Final[str] = 'filename'
SEFT_FILE: Final[str] = 'seft'
CONTEXT: Final[str] = 'context'
TX_ID: Final[str] = "tx_id"
UTF8: Final[str] = "utf-8"
SEFT_FILE_V2: Final[str] = 'seft_file'

logger = get_logger()


def deliver_seft(meta_dict: Metadata, file_bytes: bytes):
    """
    Post a seft submission to sdx-deliver.
    """
    filename = meta_dict['filename']
    tx_id = meta_dict['tx_id']

    endpoint = "deliver/v2/seft"
    context = {
        "survey_id": meta_dict["survey_id"],
        "period_id": meta_dict["period"],
        "ru_ref": meta_dict["ru_ref"],
        "tx_id": tx_id,
        "survey_type": "seft",
        "context_type": "business_survey"
    }
    context_json: str = json.dumps(context)

    sdx_app.http_post(CONFIG.DELIVER_SERVICE_URL,
                      endpoint,
                      None,
                      params={FILE_NAME: filename, TX_ID: tx_id, CONTEXT: context_json},
                      files={SEFT_FILE_V2: file_bytes})
