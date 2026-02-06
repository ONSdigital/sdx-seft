import json
from typing import Final, Protocol

import requests

from app import get_logger
from app.config.deliver_config import DeliverConfigDetails
from app.definitions.definitions import Metadata, SurveyType

logger = get_logger()


METADATA_FILE: Final[str] = 'metadata'
FILE_NAME: Final[str] = 'filename'
CONTEXT: Final[str] = 'context'
TX_ID: Final[str] = "tx_id"


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

    def __init__(self,
                 settings: SettingsProtocol,
                 http_service: HttpProtocol,
                 deliver_config: dict[SurveyType, DeliverConfigDetails]):
        self._settings = settings
        self._http_service = http_service
        self._deliver_config = deliver_config

    def deliver(self, survey_type: SurveyType, meta_dict: Metadata, filename: str, file_bytes: bytes):
        """
        Post a submission to sdx-deliver
        :param survey_type: Survey type
        :param meta_dict: Metadata dictionary
        :param filename: filename
        :param file_bytes: file bytes
        """
        tx_id = meta_dict['tx_id']

        endpoint = self._deliver_config[survey_type]['endpoint']
        file_key = self._deliver_config[survey_type]['file_key']
        context = {
            "survey_id": meta_dict["survey_id"],
            "period_id": meta_dict["period"],
            "ru_ref": meta_dict["ru_ref"],
            "tx_id": tx_id,
            "survey_type": survey_type,
            "context_type": "business_survey"
        }
        context_json: str = json.dumps(context)

        # Post to sdx-deliver
        self._http_service.post(
            self._settings.deliver_service_url,
            endpoint,
            params={FILE_NAME: filename, TX_ID: tx_id, CONTEXT: context_json},
            files={file_key: file_bytes}
        )
