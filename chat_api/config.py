import os

DEFAULT = dict(
    APP_NAME="ai-chat",
    DATABASE_URL="postgresql://admin:chatAdmin@localhost:5435/ai_chat",
    OPENPECHA_AI_URL="https://buddhist-consensus.onrender.com/api/chat/stream",
    MAX_QUERY_LENGTH=2000
)

def get(key: str) -> str:
    if key in os.environ:
        return os.environ[key]
    else:
        return str(DEFAULT[key])
