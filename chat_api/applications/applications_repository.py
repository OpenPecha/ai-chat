from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from chat_api.applications.models import Application

def get_application_by_name(db: Session, name: str) -> Application:
    return db.execute(select(Application).where(Application.name == name)).scalar_one()
