from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session
from uuid import UUID

from chat_api.threads.models import Thread
from chat_api.threads.threads_request_model import ThreadCreateRequest, ThreadCreatePayload

def create_thread(db: Session, application_id: UUID, thread_request: ThreadCreateRequest) -> Thread:

    thread = Thread(
        email=thread_request.email,
        device_type=thread_request.device_type,
        application_id=application_id
    )
    db.add(thread)
    db.commit()
    db.refresh(thread)
    return thread


