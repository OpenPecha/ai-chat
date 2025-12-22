from fastapi import FastAPI

from chat_api.views.hello import router as hello_router
from chat_api.threads.thread_views import thread_router

api = FastAPI(title="ai-chat")
api.include_router(hello_router)
api.include_router(thread_router)