from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class ApplicationResponse(BaseModel):
    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime

class ApplicationCreateRequest(BaseModel):
    name: str