from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from chat_api.chats.chats_services import get_chat_stream
from chat_api.chats.chats_reponse_model import ChatRequest



chats_router = APIRouter(
    prefix="/chats",
    tags=["Chats"]
)

@chats_router.post("")
async def get_chats(chat_request: ChatRequest):
    return StreamingResponse(
        get_chat_stream(chat_request),
        media_type="text/event-stream"
    )