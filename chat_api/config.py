import os

DEFAULT = dict(
    APP_NAME="ai-chat",
    DATABASE_URL="postgresql://admin:chatAdmin@localhost:5434/ai_chat"
)

def get(key: str) -> str:
    if key in os.environ:
        return os.environ[key]
    else:
        return str(DEFAULT[key])
