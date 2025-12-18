from chat_api.config import get
import httpx
from chat_api.chats.chats_reponse_model import ChatRequest, ChatUserQuery, chatRequestPayload
from chat_api.error_contant import ErrorConstant,ResponseError
from fastapi import HTTPException


async def get_chat_stream(chat_request: ChatRequest):

    user_query = ChatUserQuery(role="user", content=chat_request.query)
    chat_request_payload = chatRequestPayload(messages=[user_query]).model_dump()
    url = get("OPENPECHA_AI_URL")
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, read=120.0)) as client:
        async with client.stream("POST", url, json=chat_request_payload) as response:
            # Stream the response chunks
            async for chunk in response.aiter_bytes():
                if chunk:
                    yield chunk