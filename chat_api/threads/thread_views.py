from fastapi import APIRouter, Depends
from uuid import UUID
from sqlalchemy.orm import Session
from typing import Optional

from chat_api.db.db import SessionLocal
from chat_api.threads.thread_repository import ThreadRepository
from chat_api.threads.thread_service import ThreadService
from chat_api.threads.thread_response_model import ThreadResponse, ThreadsListResponse


thread_router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@thread_router.get("/threads/{thread_id}", response_model=ThreadResponse)
def get_thread(thread_id: UUID, db: Session = Depends(get_db)):
    repository = ThreadRepository(db)
    service = ThreadService(repository)
    return service.get_thread_by_id(thread_id)


@thread_router.get("/threads", response_model=ThreadsListResponse)
def get_all_threads(
    email: Optional[str] = None,
    application: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    repository = ThreadRepository(db)
    service = ThreadService(repository)
    return service.get_all_threads(email=email, application=application, skip=skip, limit=limit)

@thread_router.delete("/threads/{thread_id}")
def delete_thread(thread_id: UUID, db: Session = Depends(get_db)):
    repository = ThreadRepository(db)
    service = ThreadService(repository)
    return service.delete_thread_by_id(thread_id)
