from chat_api.config import get
import httpx
import json

from chat_api.chats.chats_reponse_model import ChatRequest, ChatUserQuery, chatRequestPayload, ChatResponsePayload
from chat_api.error_contant import ErrorConstant,ResponseError
from fastapi import HTTPException

from chat_api.chats.models import Chat
from chat_api.db import SessionLocal
from chat_api.chats.chats_repository import save_chat

from chat_api.threads.threads_services import create_thread
from chat_api.threads.threads_request_model import ThreadCreateRequest

async def get_chat_stream(chat_request: ChatRequest):

    user_query = ChatUserQuery(role="user", content=chat_request.query)
    chat_request_payload = chatRequestPayload(messages=[user_query]).model_dump()
    url = get("OPENPECHA_AI_URL")
    chat_list = []
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, read=120.0)) as client:
        async with client.stream("POST", url, json=chat_request_payload) as response:
            # Stream the response chunks
            async for chunk in response.aiter_lines():
                if chunk:
                    stripped_chunk = chunk[len("data:"):].strip()
                    obj = json.loads(stripped_chunk)
                    if obj is not None:
                        chat_list.append(obj)
                    yield chunk

        
            if len(chat_list) > 0:
                if chat_request.thread_id is None:
                    thread_request = ThreadCreateRequest(email=chat_request.email, device_type=chat_request.device_type, application_name=chat_request.application)
                    thread = create_thread(thread_request=thread_request)

                thread_id = chat_request.thread_id if chat_request.thread_id else thread.id

                response_payload = ChatResponsePayload(thread_id=thread_id, response=chat_list, question=chat_request.query)
                await save_chat(response_payload=response_payload)
            yield json.dumps({"thread_id": "hello this is thread id"})
    
    