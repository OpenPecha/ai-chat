from fastapi import FastAPI

from chat_api.applications.models import Application
from chat_api.threads.models import Thread
from chat_api.chats.models import Chat

from chat_api.threads.thread_views import thread_router

api = FastAPI(title="ai-chat")
api.include_router(thread_router)