from chat_api.config import get
import httpx
import json
from typing import Optional

from chat_api.chats.chats_reponse_model import ChatRequest, ChatUserQuery, chatRequestPayload, ChatResponsePayload
from chat_api.error_contant import ErrorConstant,ResponseError
from fastapi import HTTPException

from chat_api.chats.models import Chat
from chat_api.db import SessionLocal
from chat_api.chats.chats_repository import save_chat

from chat_api.threads.thread_service import create_thread
from chat_api.threads.threads_request_model import ThreadCreateRequest
from chat_api.auth_utils import get_user_email_from_token

def merge_token_items(chat_list: list) -> list:
    merged_data = []
    token_data = ""
    done_item = None
    
    for item in chat_list:
        if item.get("type") == "token":
            token_data += item.get("data", "")
        elif item.get("type") == "done":
            done_item = item
        else:
            merged_data.append(item)
    
    if token_data:
        merged_data.append({"data": token_data, "type": "token"})
    
    if done_item:
        merged_data.append(done_item)
    
    return merged_data

async def get_chat_stream(token: str, chat_request: ChatRequest):
    email = get_user_email_from_token(token)

    user_query = ChatUserQuery(role="user", content=chat_request.query)
    chat_request_payload = chatRequestPayload(messages=[user_query]).model_dump()
    url = get("OPENPECHA_AI_URL")
    chat_list = []
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, read=120.0)) as client:
        async with client.stream("POST", url, json=chat_request_payload) as response:
            # Stream the response chunks
            async for line in response.aiter_lines():
                frame = sse_frame_from_line(line, on_json=chat_list.append)
                if frame:
                    yield frame    
        
            if len(chat_list) > 0:
                if chat_request.thread_id is None:
                    thread_request = ThreadCreateRequest(email=email, device_type=chat_request.device_type, application_name=chat_request.application)
                    thread = create_thread(thread_request=thread_request)

                thread_id = chat_request.thread_id if chat_request.thread_id else thread.id
                with SessionLocal() as db_session:
                    merged_chat_list = merge_token_items(chat_list)
                    response_payload = ChatResponsePayload(thread_id=thread_id, response=merged_chat_list, question=chat_request.query)
                    save_chat(db_session, response_payload=response_payload)

        yield (
            f"data: {json.dumps({'thread_id': str(thread_id)})}\n\n"
        ).encode("utf-8")

def sse_frame_from_line(
    line: str,
    on_json: list[dict] = [],
) -> Optional[bytes]:

    if not line:
        return None

    line = line.strip()
    if not line:
        return None

    if line.startswith(":"):
        return (line + "\n\n").encode("utf-8")

    payload = line[len("data:") :].strip() if line.startswith("data:") else line
    on_json(json.loads(payload))
    return (f"data: {payload}\n\n").encode("utf-8")
    