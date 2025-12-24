from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from chat_api.threads.models import DeviceType


class ThreadCreateRequest(BaseModel):
    email: str = Field(min_length=1)
    device_type: DeviceType
    application_name: str

class ThreadCreatePayload(BaseModel):
    email: str = Field(min_length=1)
    device_type: DeviceType
    application_id: UUID


class ThreadResponse(BaseModel):
    id: str
    email: str
    device_type: DeviceType
    application_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool


