from fastapi import Depends
from sdx_base.services.http import HttpService
from sdx_base.services.pubsub import PubsubService
from sdx_base.services.storage import StorageService

from app.config.deliver_config import deliver_config
from app.services.deliver_service import DeliverService
from app.services.process_service import ProcessService
from app.services.receipt_service import ReceiptService
from app.settings import Settings, get_instance


def get_settings() -> Settings:
    return get_instance()


def get_http_service() -> HttpService:
    return HttpService()


def get_storage_service() -> StorageService:
    return StorageService()


def get_pubsub_service() -> PubsubService:
    return PubsubService()


def get_deliver_service(
        settings: Settings = Depends(get_settings),
        http_service: HttpService = Depends(get_http_service)
) -> DeliverService:
    return DeliverService(settings, http_service, deliver_config)


def get_process_service(
        settings: Settings = Depends(get_settings),
        storage: StorageService = Depends(get_storage_service),
        deliver: DeliverService = Depends(get_deliver_service),
        pubsub: PubsubService = Depends(get_pubsub_service),
) -> ProcessService:
    return ProcessService(settings, storage, deliver, pubsub)


def get_receipt_service(
    deliver: DeliverService = Depends(get_deliver_service),
) -> ReceiptService:
    return ReceiptService(deliver)
