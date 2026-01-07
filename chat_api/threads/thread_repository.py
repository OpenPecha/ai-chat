from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List, Tuple

from chat_api.threads.models import Thread


def get_thread_by_id(db: Session, thread_id: UUID) -> Optional[Thread]:
    return (
        db.query(Thread)
        .options(joinedload(Thread.chats))
        .filter(Thread.id == thread_id, Thread.is_deleted == False)
        .first()
    )


def get_threads(
    db: Session,
    email: str,
    application: str,
    skip: int = 0, 
    limit: int = 10
) -> Tuple[List[Thread], int]:
    query = db.query(Thread).filter(
        Thread.is_deleted == False,
        Thread.email == email
    ).join(Thread.application).filter(Thread.application.has(name=application))
    
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


def soft_delete_thread(db: Session, thread_id: UUID) -> bool:
    thread = db.query(Thread).filter(
        Thread.id == thread_id
    ).first()
    
    if thread:
        thread.is_deleted = True
        db.commit()
        return True
    return False