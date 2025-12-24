from chat_api.applications.applications_repository import get_application_by_name
from chat_api.applications.models import Application
from fastapi import HTTPException
from chat_api.db import SessionLocal

def get_application_by_name_service(db: SessionLocal(), name: str) -> Application:

    with SessionLocal() as db_session:
        application = get_application_by_name(db_session, name=name)
        if application is None:
            raise HTTPException(status_code=404, detail="Application not found")
        return application

