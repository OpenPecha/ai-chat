from fastapi import FastAPI

from chat_api.views.hello import router as hello_router
from chat_api.chats.chats_views import chats_router
from chat_api.applications.application_views import applications_router

api = FastAPI(title="ai-chat")
api.include_router(hello_router)
api.include_router(chats_router)
api.include_router(applications_router)
