from fastapi import Depends
from sdx_base.services.http import HttpService
from sdx_base.services.storage import StorageService
from sdx_base.settings.app import get_settings

from app.services.deliver_service import DeliverService
from app.services.process_service import ProcessService
from app.settings import Settings


def get_http_service() -> HttpService:
    return HttpService()


def get_storage_service() -> StorageService:
    return StorageService()


def get_deliver_service(
        settings: Settings = Depends(get_settings),
        http_service: HttpService = Depends(get_http_service)
) -> DeliverService:
    return DeliverService(settings, http_service)


def get_process_service(
        settings: Settings = Depends(get_settings),
        storage: StorageService = Depends(get_storage_service),
        deliver: DeliverService = Depends(get_deliver_service),
) -> ProcessService:
    return ProcessService(settings, storage, deliver)
