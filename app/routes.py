
from fastapi import APIRouter, Depends
from sdx_base.errors.errors import DataError
from sdx_base.models.pubsub import Message, get_message
from starlette.requests import Request
from starlette.responses import Response

from app.dependencies import get_process_service
from app.services.process_service import ProcessService

router = APIRouter()


@router.post("/")
async def handle(
        request: Request,
        process_service: ProcessService = Depends(get_process_service)) -> Response:

    # Fetch the Pub/Sub message
    message: Message = await get_message(request)

    try:
        # Process the message
        process_service.process_message(message)
    except DataError as e:
        quarantine_reason = f"DataError: {str(e)}"
        process_service.quarantine_message(message, quarantine_reason)

    return Response(status_code=204)
