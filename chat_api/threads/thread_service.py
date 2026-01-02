from uuid import UUID
from typing import Optional, List
from fastapi import HTTPException

from chat_api.threads.thread_repository import ThreadRepository
from chat_api.threads.thread_response_model import ThreadResponse, Message, SearchResult
from chat_api.chats.models import Chat


class ThreadService:
    def __init__(self, repository: ThreadRepository):
        self.repository = repository

    def get_thread_by_id(self, thread_id: UUID) -> ThreadResponse:
        thread = self.repository.get_thread_by_id(thread_id)
        
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        messages = self.transform_chats_to_messages(thread.chats)
        
        title = thread.chats[0].question if thread.chats else "Untitled Thread"
        
        return ThreadResponse(
            id=thread.id,
            title=title,
            messages=messages
        )

    def transform_chats_to_messages(self, chats: List[Chat]) -> List[Message]:
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
            
            if isinstance(chat.response, dict):
                answer = chat.response.get("answer", "")
                search_results_data = chat.response.get("search_results", [])
                
                search_results = [
                    SearchResult(
                        id=sr.get("id", ""),
                        title=sr.get("title", ""),
                        text=sr.get("text", "")
                    )
                    for sr in search_results_data
                ] if search_results_data else None
                
                assistant_message = Message(
                    role="assistant",
                    content=answer,
                    id=chat.id,
                    searchResults=search_results
                )
                messages.append(assistant_message)
        
        return messages

    def delete_thread_by_id(self, thread_id: UUID) -> dict:
        deleted = self.repository.soft_delete_thread(thread_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Thread not found or already deleted")
        
        return {"message": "Thread deleted successfully", "thread_id": str(thread_id)}
