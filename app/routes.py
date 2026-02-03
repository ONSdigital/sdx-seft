
from fastapi import APIRouter, Depends
from sdx_base.errors.errors import DataError
from sdx_base.models.pubsub import Message, get_message, get_data
from starlette.requests import Request
from starlette.responses import Response

from app.definitions.definitions import Metadata
from app.dependencies import get_process_service, get_receipt_service
from app.services.process_service import ProcessService
from app.services.receipt_service import ReceiptService

router = APIRouter()


@router.post("/")
async def handle(
        request: Request,
        process_service: ProcessService = Depends(get_process_service),
        receipt_service: ReceiptService = Depends(get_receipt_service),
) -> Response:

    # Fetch the Pub/Sub message
    message: Message = await get_message(request)
    meta_dict: Metadata = {}

    try:
        # Extract metadata from the message
        meta_dict = process_service.process_metadata(message)
        # Process the message and deliver the SEF file
        process_service.process_seft(message)
    except DataError as e:
        process_service.quarantine_message(message, str(e))
        # Ack message (even in case of error, as it has been quarantined)
        return Response(status_code=204)

    # Process the receipt for SEFT file
    receipt_service.process_receipt(meta_dict)

    # Ack message
    return Response(status_code=204)
