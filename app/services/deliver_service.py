import json
from typing import Final

from sdx_base.services.http import HttpService

from app import get_logger
from app.definitions import Metadata
from app.settings import Settings

logger = get_logger()


METADATA_FILE: Final[str] = 'metadata'
FILE_NAME: Final[str] = 'filename'
CONTEXT: Final[str] = 'context'
TX_ID: Final[str] = "tx_id"
SEFT_FILE_V2: Final[str] = 'seft_file'


class DeliverService:

    def __init__(self, settings: Settings, http_service: HttpService):

        self._settings = settings
        # TODO make this protocol
        self._http_service = http_service

    def deliver_seft(self, meta_dict: Metadata, file_bytes: bytes):
        """
        Post a seft submission to sdx-deliver
        :param meta_dict: Metadata dictionary
        :param file_bytes: SEFT file bytes
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

        # Post to sdx-deliver
        self._http_service.post(
            self._settings.deliver_service_url,
            endpoint,
            params={FILE_NAME: filename, TX_ID: tx_id, CONTEXT: context_json},
            files={SEFT_FILE_V2: file_bytes}
        )
