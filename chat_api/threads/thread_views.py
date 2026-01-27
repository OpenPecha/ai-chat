from fastapi import APIRouter, Depends
from uuid import UUID
from sqlalchemy.orm import Session

from chat_api.db.database import SessionLocal
from chat_api.threads.thread_repository import ThreadRepository
from chat_api.threads.thread_service import ThreadService
from chat_api.threads.thread_response_model import ThreadResponse


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