from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from chat_api.applications.models import Application
from chat_api.threads.models import DeviceType, Thread


def get_or_create_application(db: Session, *, name: str) -> Application:
    existing = db.execute(select(Application).where(Application.name == name)).scalar_one_or_none()
    if existing is not None:
        return existing

    application = Application(name=name)
    db.add(application)
    # Flush so `application.id` is available for the thread FK without committing yet.
    db.flush()
    return application


def create_thread(
    db: Session,
    *,
    email: str,
    device_type: DeviceType,
    application_name: Optional[str] = None,
) -> Thread:
    application: Optional[Application] = None
    if application_name:
        application = get_or_create_application(db, name=application_name)

    thread = Thread(
        email=email,
        device_type=device_type,
        application_id=application.id if application else None,
    )
    db.add(thread)
    return thread


