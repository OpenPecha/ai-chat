from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from chat_api.applications.models import Application
from chat_api.applications.applications_response_models import ApplicationCreateRequest

def get_application_by_name(db: Session, name: str) -> Application:
    return db.execute(select(Application).where(Application.name == name)).scalar_one()

def create_application_repo(db: Session, application: ApplicationCreateRequest) -> Application:
    db_application = Application(name=application.name)
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application
