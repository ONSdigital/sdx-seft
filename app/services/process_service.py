import json

from sdx_base.errors.errors import DataError
from sdx_base.models.pubsub import Message, get_data
from sdx_base.services.storage import StorageService

from app import get_logger
from app.services.deliver_service import DeliverService
from app.settings import Settings

logger = get_logger()


class ProcessService:

    def __init__(self,
                 settings: Settings,
                 storage_service: StorageService,
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
