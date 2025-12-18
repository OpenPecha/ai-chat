from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from chat_api.chats.chats_services import get_chat_stream



chats_router = APIRouter(
    prefix="/chats",
    tags=["Chats"]
)

@chats_router.post("")
async def get_chats(email: str, query: str):
    return StreamingResponse(
        get_chat_stream(email, query),
        media_type="text/event-stream"
    )