from fastapi import FastAPI

from chat_api.views.hello import router as hello_router

api = FastAPI(title="ai-chat")
api.include_router(hello_router)


