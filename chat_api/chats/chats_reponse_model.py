from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    email: str
    query: str

class ChatUserQuery(BaseModel):
    role: str
    content: str

class chatRequestPayload(BaseModel):
    messages: List[ChatUserQuery]

