from chat_api.chats.models import Chat
from chat_api.db import SessionLocal
from chat_api.chats.chats_reponse_model import ChatResponsePayload

def save_chat(response_payload: ChatResponsePayload):
    db.add(response_payload)
    db.commit()
    db.refresh(response_payload)
    return response_payload