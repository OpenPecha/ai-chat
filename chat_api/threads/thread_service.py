from uuid import UUID
from typing import Optional, List, Dict, Any
from fastapi import HTTPException

from chat_api.threads.thread_repository import ThreadRepository
from chat_api.threads.thread_response_model import ThreadResponse, Message, SearchResult
from chat_api.chats.models import Chat


class ThreadService:
    def __init__(self, repository: ThreadRepository):
        self.repository = repository

    def get_all_threads(
        self, 
        email: Optional[str] = None, 
        application: Optional[str] = None,
        skip: int = 0, 
        limit: int = 10
    ) -> Dict[str, Any]:

        threads, total = self.repository.get_threads(email, application, skip, limit)
        
        thread_data = []
        for thread in threads:
            if thread.chats:
                first_chat = min(thread.chats, key=lambda chat: chat.created_at)
                title = first_chat.question
            else:
                title = "Untitled Thread"
            
            thread_data.append({
                "id": str(thread.id),
                "title": title
            })
        
        return {
            "data": thread_data,
            "total": total
        }

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
            
            if isinstance(chat.response, list):
                answer = ""
                search_results = None
                
                for item in chat.response:
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
                
                assistant_message = Message(
                    role="assistant",
                    content=answer,
                    id=chat.id,
                    searchResults=search_results
                )
                messages.append(assistant_message)
            elif isinstance(chat.response, dict):
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
