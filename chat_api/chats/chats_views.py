from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from chat_api.chats.chats_services import get_chat_stream
from chat_api.chats.chats_reponse_model import ChatRequest
from chat_api.config import get
from fastapi import HTTPException
from chat_api.error_constants import ErrorConstants, ResponseError



chats_router = APIRouter(
    prefix="/chats",
    tags=["Chats"]
)

@chats_router.post("")
def get_chats(chat_request: ChatRequest) -> StreamingResponse:

    max_query_length = get("MAX_QUERY_LENGTH")
    if len(chat_request.query) > int(max_query_length):
        raise HTTPException(status_code=400, detail=ResponseError(error=ErrorConstants.BAD_REQUEST, message=ErrorConstants.MAX_QUERY_LENGTH_ERROR).model_dump())
    
    return StreamingResponse(
        get_chat_stream(chat_request),
        media_type="text/event-stream"
    )