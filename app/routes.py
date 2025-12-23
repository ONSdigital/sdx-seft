
from fastapi import APIRouter, Depends
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

    # Process the message # TODO check if data error is handled here or in BASE
    process_service.process_message(message)

    return Response(status_code=204)
