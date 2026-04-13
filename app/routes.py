import base64
import json

from fastapi import APIRouter, Depends
from sdx_base.errors.errors import DataError
from sdx_base.models.pubsub import Message, get_message, get_data
from starlette.requests import Request
from starlette.responses import Response

from app.definitions.definitions import Metadata
from app.dependencies import get_process_service, get_receipt_service
from app.functions.filename_function import parse_metadata_from_filename
from app.services.process_service import ProcessService
from app.services.receipt_service import ReceiptService

router = APIRouter()


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

    data: str = base64.b64decode(content).decode("utf-8").strip()
    data: dict = json.loads(data)

    file_name = data["name"]

    # Work out other metadata from file_name
    metadata: Metadata | None = parse_metadata_from_filename(file_name)

    if not metadata:
        raise DataError("Failed to parse metadata from filename!")

    try:
        process_service.process_seft(metadata)
    except DataError as e:

        # TODO fix this
        process_service.quarantine_message(message, str(e))
        # Ack message (even in case of error, as it has been quarantined)
        return Response(status_code=204)

    # Process the receipt for SEFT file
    receipt_service.process_receipt(metadata)

    # Ack message
    return Response(status_code=204)
