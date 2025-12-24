from chat_api.chats.models import Chat
from chat_api.chats.chats_reponse_model import ChatResponsePayload
from sqlalchemy.orm import Session

def save_chat(db: Session, response_payload: ChatResponsePayload):
    chat = Chat(
        thread_id=response_payload.thread_id,
        response=response_payload.response,
        question=response_payload.question
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat