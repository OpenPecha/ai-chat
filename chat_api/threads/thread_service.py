from uuid import UUID
from typing import Optional, List, Dict, Any
from fastapi import HTTPException
from starlette import status
import logging

from chat_api.db.db import SessionLocal

logger = logging.getLogger(__name__)
from chat_api.threads import thread_repository
from chat_api.threads.thread_response_model import ThreadResponse, Message, SearchResult, ThreadListResponse, ResponseError
from chat_api.threads.thread_enums import MessageRole
from chat_api.threads.models import Thread
from chat_api.chats.models import Chat
from chat_api.auth_utils import get_user_email_from_token
from chat_api.response_message import THREAD_NOT_FOUND, BAD_REQUEST, UNTITLED_THREAD
from chat_api.threads.thread_request_models import ThreadCreateRequest
from chat_api.applications.applications_services import get_application_by_name_service


def create_thread(thread_request: ThreadCreateRequest) -> ThreadResponse:
    with SessionLocal() as db_session:
        application = get_application_by_name_service(db_session, name=thread_request.application_name)
        if application is None:
            raise HTTPException(status_code=404, detail="Application not found")
        thread = thread_repository.create_thread(db_session, application_id=application.id, thread_request=thread_request)
        return thread


async def get_all_threads(
    token: str,
    application: str,
    skip: int = 0, 
    limit: int = 10
) -> ThreadListResponse:
    email = get_user_email_from_token(token)
    
    with SessionLocal() as db:
        threads, total = thread_repository.get_threads(db, email, application, skip, limit)
        
        thread_data = []
        for thread in threads:
            title = extract_thread_title(thread)
            thread_data.append({
                "id": str(thread.id),
                "title": title
            })
        
        return ThreadListResponse(
            data=thread_data,
            total=total
        )

async def get_thread_by_id(token: str, thread_id: UUID) -> ThreadResponse:
    get_user_email_from_token(token)
    
    with SessionLocal() as db:
        thread = thread_repository.get_thread_by_id(db, thread_id)
        
        if not thread:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ResponseError(error=BAD_REQUEST, message=THREAD_NOT_FOUND).model_dump()
            )
        
        sorted_chats = sorted(thread.chats, key=lambda x: x.created_at) if thread.chats else []
        title = sorted_chats[0].question if sorted_chats else UNTITLED_THREAD
        messages = transform_chats_to_messages_from_sorted(sorted_chats)
        
        return ThreadResponse(
            id=thread.id,
            title=title,
            messages=messages
        )

async def delete_thread_by_id(token: str, thread_id: UUID) -> None:
    get_user_email_from_token(token)
    
    with SessionLocal() as db:
        rows_updated = thread_repository.delete_thread_by_id(db, thread_id)
        
        if rows_updated == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ResponseError(error=BAD_REQUEST, message=THREAD_NOT_FOUND).model_dump()
            )

def extract_thread_title(thread: Thread) -> str:

    if thread.chats:
        first_chat = min(thread.chats, key=lambda chat: chat.created_at)
        return first_chat.question
    return UNTITLED_THREAD


def transform_chats_to_messages(chats: List[Chat]) -> List[Message]:
    sorted_chats = sorted(chats, key=lambda x: x.created_at)
    return transform_chats_to_messages_from_sorted(sorted_chats)


def transform_chats_to_messages_from_sorted(sorted_chats: List[Chat]) -> List[Message]:
    messages = []
    
    for chat in sorted_chats:
        user_message = Message(
            role=MessageRole.USER,
            content=chat.question,
            id=chat.id,
            searchResults=None
        )
        messages.append(user_message)
        
        if isinstance(chat.response, list):
            answer, search_results = parse_list_response(chat.response)
        elif isinstance(chat.response, dict):
            answer, search_results = parse_dict_response(chat.response)
        else:
            logger.warning(f"Invalid response format for chat {chat.id}: {type(chat.response)}")
            continue
        
        assistant_message = Message(
            role=MessageRole.ASSISTANT,
            content=answer,
            id=chat.id,
            searchResults=search_results
        )
        messages.append(assistant_message)
    
    return messages


def parse_list_response(response: List[Dict]) -> tuple[str, Optional[List[SearchResult]]]:
    answer = ""
    search_results = None
    
    for item in response:
        if item.get("type") == "token":
            answer = item.get("data", "")
        elif item.get("type") == "search_results":
            search_results_data = item.get("data", [])
            search_results = [
                SearchResult(
                    id=sr.get("id", ""),
                    title=sr.get("title", ""),
                    text=sr.get("text", "")
                )
                for sr in search_results_data
            ] if search_results_data else None
    
    return answer, search_results


def parse_dict_response(response: Dict) -> tuple[str, Optional[List[SearchResult]]]:
    answer = response.get("answer", "")
    search_results_data = response.get("search_results", [])
    
    search_results = [
        SearchResult(
            id=sr.get("id", ""),
            title=sr.get("title", ""),
            text=sr.get("text", "")
        )
        for sr in search_results_data
    ] if search_results_data else None
    
    return answer, search_results
