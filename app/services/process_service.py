import json
from typing import Protocol, Optional

from sdx_base.errors.errors import DataError
from sdx_base.models.pubsub import Message, get_data

from app import get_logger
from app.definitions.definitions import Metadata, SurveyType
from app.services.deliver_service import DeliverService

logger = get_logger()


class ReadProtocol(Protocol):
    def read(self,
             filename: str,
             bucket_name: str,
             sub_dir: Optional[str] = None,
             project_id: Optional[str] = None) -> bytes:
        ...


class SettingsProtocol(Protocol):
    project_id: str
    quarantine_topic_id: str

    def get_bucket_name(self) -> str:
        ...


class PubsubProtocol(Protocol):

    def quarantine_error(self, quarantine_topic_path: str, error: Exception, message: str, tx_id: str) -> str:
        ...


class ProcessService:

    def __init__(self,
                 settings: SettingsProtocol,
                 storage_service: ReadProtocol,
                 deliver_service: DeliverService,
                 pubsub_service: PubsubProtocol
                 ):
        self._settings = settings
        self._storage_service = storage_service
        self._deliver_service = deliver_service
        self._pubsub_service = pubsub_service

    def process_message(self, message: Message) -> Metadata:

        # Decode the Pub/Sub message data
        data: str = get_data(message)
        logger.info(f"Seft triggered by PubSub message with data: {data}")

        # Check for filename in the message data
        meta_dict: Metadata = json.loads(data)
        if "filename" not in meta_dict:
            raise DataError("Missing filename from data!")

        # Extract the data from GCP
        filename = meta_dict.get("filename")
        data_bytes = self._storage_service.read(filename, self._settings.get_bucket_name())

        # Deliver the SEFT file
        self._deliver_service.deliver(SurveyType.SEFT, meta_dict, filename, data_bytes)

        logger.info("SEFT file process completed successfully")

        return meta_dict

    def quarantine_message(self, message: Message, reason: str):

        # Decode the Pub/Sub message data
        data: str = get_data(message)

        # Extract the tx_id
        tx_id = json.loads(data)["tx_id"]

        logger.info(f"Quarantining message with data: {data} for reason: {reason}")
        self._pubsub_service.quarantine_error(
            f"projects/{self._settings.project_id}/topics/{self._settings.quarantine_topic_id}",
            DataError,
            reason,
            tx_id
        )
        logger.info("Quarantine completed successfully")
