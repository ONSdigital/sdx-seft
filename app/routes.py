from fastapi import APIRouter, Depends
from sdx_base.errors.errors import DataError, UnrecoverableError
from sdx_base.models.pubsub import Message, get_message
from starlette.requests import Request
from starlette.responses import Response

from app import get_logger
from app.definitions.definitions import Metadata
from app.dependencies import get_process_service, get_receipt_service
from app.functions.filename_function import parse_metadata_from_filename
from app.services.process_service import ProcessService
from app.services.receipt_service import ReceiptService

router = APIRouter()

logger = get_logger()


@router.post("/")
async def handle(
    request: Request,
    process_service: ProcessService = Depends(get_process_service),
    receipt_service: ReceiptService = Depends(get_receipt_service),
) -> Response:

    # Extract the filename from the request
    message: Message = await get_message(request)
    file_name = message["attributes"]["objectId"]
    logger.info(f"Processing file_name: {file_name}")

    # Extract metadata from the filename
    try:
        metadata: Metadata = parse_metadata_from_filename(file_name)
    except DataError:
        logger.exception(f"Could not extract metadata from filename {file_name}")

        # If an error occurs extracting metadata, we cannot quarantine, as we don't have a tx_id
        return Response(status_code=400)

    logger.info(f"Processing metadata: {metadata}")

    # Process the seft
    try:
        process_service.process_seft(metadata)
    except UnrecoverableError as e:
        logger.exception("Error processing SEFT, quarantining...")
        process_service.quarantine_seft(metadata["tx_id"], str(e))
        # Ack message (even in case of error, as it has been quarantined)
        return Response(status_code=204)

    # Process the receipt
    receipt_service.process_receipt(metadata)

    # Ack message
    return Response(status_code=204)
