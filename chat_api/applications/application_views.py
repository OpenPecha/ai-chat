from fastapi import APIRouter
from chat_api.applications.application_response_models import ApplicationCreateRequest, ApplicationResponse
from chat_api.applications.applications_services import create_application_service

router = APIRouter()


applications_router = APIRouter(
    prefix="/applications",
)

@applications_router.post("")
def create_application(application: ApplicationCreateRequest) -> ApplicationResponse:
    return create_application_service(application=application)