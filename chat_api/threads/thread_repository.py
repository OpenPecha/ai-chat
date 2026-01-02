from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List, Tuple

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
    
    def get_threads(
        self, 
        email: Optional[str] = None, 
        application: Optional[str] = None,
        skip: int = 0, 
        limit: int = 10
    ) -> Tuple[List[Thread], int]:

        query = self.db.query(Thread).filter(Thread.is_deleted == False)
        
        if email:
            query = query.filter(Thread.email == email)
        
        if application:
            query = query.join(Thread.application).filter(Thread.application.has(name=application))
        
        total = query.count()
        
        threads = (
            query
            .options(joinedload(Thread.chats))
            .order_by(Thread.updated_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return threads, total

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

