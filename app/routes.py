import base64
import json

from fastapi import APIRouter, Depends
from sdx_base.errors.errors import DataError
from sdx_base.models.pubsub import Message, get_message, get_data
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

    # TODO no idea if this will work

    # Fetch the content
    content = await request.json()

    # Extract data from request

    data: dict = json.loads(content)

    file_name = data["name"]

    # Work out other metadata from file_name
    metadata: Metadata | None = parse_metadata_from_filename(file_name)

    if not metadata:
        raise DataError("Failed to parse metadata from filename!")

    try:
        logger.info(f"Received metadata: {metadata}")
        process_service.process_seft(metadata)
    except DataError as e:

        # TODO fix this
        process_service.quarantine_seft(metadata["tx_id"], str(e))
        # Ack message (even in case of error, as it has been quarantined)
        return Response(status_code=204)

    receipt_service.process_receipt(metadata)

    # Ack message
    return Response(status_code=204)
