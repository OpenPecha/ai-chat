from uuid import UUID
from typing import Optional, List, Dict, Any
from fastapi import HTTPException
from starlette import status

from chat_api.db.db import SessionLocal
from chat_api.threads.thread_repository import ThreadRepository
from chat_api.threads.thread_response_model import ThreadResponse, Message, SearchResult, ThreadListResponse
from chat_api.threads.models import Thread
from chat_api.chats.models import Chat


async def get_all_threads(
    email: str,
    application: str,
    skip: int = 0, 
    limit: int = 10
) -> ThreadListResponse:

    with SessionLocal() as db:
        repository = ThreadRepository(db)
        threads, total = repository.get_threads(email, application, skip, limit)
        
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

async def get_thread_by_id(thread_id: UUID) -> ThreadResponse:

    with SessionLocal() as db:
        repository = ThreadRepository(db)
        thread = repository.get_thread_by_id(thread_id)
        
        if not thread:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thread not found"
            )
        
        messages = transform_chats_to_messages(thread.chats)
        title = extract_thread_title(thread)
        
        return ThreadResponse(
            id=thread.id,
            title=title,
            messages=messages
        )

async def delete_thread_by_id(thread_id: UUID) -> None:

    with SessionLocal() as db:
        repository = ThreadRepository(db)
        deleted = repository.soft_delete_thread(thread_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND
            )


def extract_thread_title(thread: Thread) -> str:

    if thread.chats:
        first_chat = min(thread.chats, key=lambda chat: chat.created_at)
        return first_chat.question
    return "Untitled Thread"


def transform_chats_to_messages(chats: List[Chat]) -> List[Message]:

    messages = []
    sorted_chats = sorted(chats, key=lambda x: x.created_at)
    
    for chat in sorted_chats:
        user_message = Message(
            role="user",
            content=chat.question,
            id=chat.id,
            searchResults=None
        )
        messages.append(user_message)
        
        if isinstance(chat.response, list):
            answer, search_results = parse_list_response(chat.response)
            assistant_message = Message(
                role="assistant",
                content=answer,
                id=chat.id,
                searchResults=search_results
            )
            messages.append(assistant_message)
        elif isinstance(chat.response, dict):
            answer, search_results = parse_dict_response(chat.response)
            assistant_message = Message(
                role="assistant",
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
