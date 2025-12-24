from chat_api.chats.models import Chat
from chat_api.chats.chats_reponse_model import ChatResponsePayload
from sqlalchemy.orm import Session

def save_chat(db: Session, response_payload: ChatResponsePayload):
    db.add(response_payload)
    db.commit()
    db.refresh(response_payload)
    return response_payload