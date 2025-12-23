import json
from typing import Protocol, Optional

from sdx_base.errors.errors import DataError
from sdx_base.models.pubsub import Message, get_data

from app import get_logger
from app.services.deliver_service import DeliverService
from app.settings import SettingsProtocol

logger = get_logger()


class ReadProtocol(Protocol):
    def read(self,
             filename: str,
             bucket_name: str,
             sub_dir: Optional[str] = None,
             project_id: Optional[str] = None) -> bytes:
        ...


class ProcessService:

    def __init__(self,
                 settings: SettingsProtocol,
                 storage_service: ReadProtocol,
                 deliver_service: DeliverService
                 ):
        self._settings = settings
        self._storage_service = storage_service
        self._deliver_service = deliver_service

    def process_message(self, message: Message):

        # Decode the Pub/Sub message data
        data: str = get_data(message)
        logger.info(f"Seft triggered by PubSub message with data: {data}")

        # Check for filename in the message data
        meta_dict = json.loads(data)
        if "filename" not in meta_dict:
            raise DataError("Missing filename from data!")

        # Extract the data from GCP
        filename = meta_dict.get("filename")
        data_bytes = self._storage_service.read(filename, self._settings.get_bucket_name())

        # Deliver the SEFT file
        self._deliver_service.deliver_seft(meta_dict, data_bytes)

        logger.info("Process completed successfully")
