from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    email: str
    query: str
    application: str
    device_type: str
    thread_id: Optional[str] = None

class ChatUserQuery(BaseModel):
    role: str
    content: str

class ChatResponsePayload(BaseModel):
    thread_id: str
    response: list
    question: str

class chatRequestPayload(BaseModel):
    messages: List[ChatUserQuery]

