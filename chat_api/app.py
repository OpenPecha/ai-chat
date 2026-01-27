from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from chat_api.applications.models import Application
from chat_api.threads.models import Thread
from chat_api.chats.models import Chat

from chat_api.threads.thread_views import thread_router
from chat_api.chats.chats_views import chats_router
from chat_api.applications.application_views import applications_router

api = FastAPI(
    title="ai-chat",
    description="AI Chat API for Pecha applications",
    root_path="/api/v1",
    redoc_url="/docs"
)
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
api.include_router(thread_router)
api.include_router(chats_router)
api.include_router(applications_router)