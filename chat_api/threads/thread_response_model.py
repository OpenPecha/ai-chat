from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

from chat_api.threads.thread_enums import MessageRole


class SearchResult(BaseModel):
    id: str
    title: str
    text: str

    class Config:
        from_attributes = True


class Message(BaseModel):
    role: MessageRole
    content: str
    id: UUID
    searchResults: Optional[List[SearchResult]] = None

    class Config:
        from_attributes = True


class ThreadResponse(BaseModel):
    id: UUID
    title: str
    messages: List[Message]

    class Config:
        from_attributes = True


class ThreadSummary(BaseModel):
    id: str
    title: str

    class Config:
        from_attributes = True


class ThreadListResponse(BaseModel):
    data: List[ThreadSummary]
    total: int

    class Config:
        from_attributes = True


class ResponseError(BaseModel):
    error: str
    message: str

    class Config:
        from_attributes = True
