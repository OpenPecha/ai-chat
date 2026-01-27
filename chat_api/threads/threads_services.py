from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from chat_api.db import SessionLocal
from chat_api.error_constants import ErrorConstants, ResponseError
from chat_api.threads.threads_repository import create_thread as create_thread_repo
from chat_api.threads.thread_request_models import ThreadCreateRequest, ThreadResponse
from chat_api.applications.applications_services import get_application_by_name_service

def create_thread(thread_request: ThreadCreateRequest) -> ThreadResponse:
    with SessionLocal() as db_session:
        application = get_application_by_name_service(db_session, name=thread_request.application_name)
        if application is None:
            raise HTTPException(status_code=404, detail="Application not found")
        thread = create_thread_repo(db_session, application_id=application.id, thread_request=thread_request)
        return thread