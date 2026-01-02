from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from typing import Optional

from chat_api.threads.models import Thread


class ThreadRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_thread_by_id(self, thread_id: UUID) -> Optional[Thread]:
        return (
            self.db.query(Thread)
            .options(joinedload(Thread.chats))
            .filter(Thread.id == thread_id, Thread.is_deleted == False)
            .first()
        )

    def soft_delete_thread(self, thread_id: UUID) -> bool:
        thread = self.db.query(Thread).filter(
            Thread.id == thread_id,
            Thread.is_deleted == False
        ).first()
        
        if thread:
            thread.is_deleted = True
            self.db.commit()
            return True
        return False
