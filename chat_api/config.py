import os

DEFAULT = dict(
    APP_NAME="ai-chat",
    DATABASE_URL="postgresql://admin:chatAdmin@localhost:5435/ai_chat",
    JWT_ALGORITHM="HS256",
    JWT_AUD="https://pecha.org",
    JWT_ISSUER="https://pecha.org",
    JWT_SECRET_KEY="",
    DOMAIN_NAME="dev-pecha-esukhai.us.auth0.com",
    CLIENT_ID=""
)

def get(key: str) -> str:
    if key in os.environ:
        return os.environ[key]
    else:
        return str(DEFAULT[key])
