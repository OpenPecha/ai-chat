from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from chat_api.db import SessionLocal
from chat_api.error_contant import ErrorConstant, ResponseError
from chat_api.threads.threads_repository import create_thread as create_thread_repo
from chat_api.threads.threads_request_model import ThreadCreateRequest, ThreadResponse


def create_thread(thread_request: ThreadCreateRequest) -> ThreadResponse:
    """
    Create a thread row in the database.

    - Commits on success
    - Rolls back on error
    - Always closes the DB session
    """
    db = SessionLocal()
    try:
        thread = create_thread_repo(
            db,
            email=thread_request.email,
            device_type=thread_request.device_type,
            application_name=thread_request.application,
        )
        db.commit()
        db.refresh(thread)
        return ThreadResponse.model_validate(thread)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=ResponseError(error=ErrorConstant.BAD_REQUEST, message=str(e.orig)).model_dump(),
        ) from e
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=ResponseError(error="Internal Server Error", message=str(e)).model_dump(),
        ) from e
    finally:
        db.close()


