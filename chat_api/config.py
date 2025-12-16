import os

DEFAULT = dict(
    app_name="ai-chat",
    database_url="postgresql://admin:chatAdmin@localhost:5434/ai_chat",
    db_echo=False,
    db_create_all=False,
)

def get(key: str) -> str:
    if key in os.environ:
        return os.environ[key]
    else:
        return str(DEFAULT[key])
