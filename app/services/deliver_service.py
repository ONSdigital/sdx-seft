import json
from typing import Final, Protocol

import requests

from app import get_logger
from app.definitions import Metadata

logger = get_logger()


METADATA_FILE: Final[str] = 'metadata'
FILE_NAME: Final[str] = 'filename'
CONTEXT: Final[str] = 'context'
TX_ID: Final[str] = "tx_id"
SEFT_FILE_V2: Final[str] = 'seft_file'


class HttpProtocol(Protocol):
    def post(self,
             domain: str,
             endpoint: str,
             json_data: str | None = None,
             params: dict[str, str] | None = None,
             files: dict[str, bytes] | None = None) -> requests.Response:
        ...


class SettingsProtocol(Protocol):
    deliver_service_url: str


class DeliverService:

    def __init__(self, settings: SettingsProtocol, http_service: HttpProtocol):

        self._settings = settings
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
