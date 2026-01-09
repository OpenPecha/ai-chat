import os
from dotenv import load_dotenv

load_dotenv()

DEFAULTS = dict(
    APP_NAME="ai-chat",
    DATABASE_URL="postgresql://admin:chatAdmin@localhost:5435/ai_chat",
    
    JWT_ALGORITHM="HS256",
    JWT_AUD="https://pecha-v2.org",
    JWT_ISSUER="https://pecha-v2.org",
    JWT_SECRET_KEY="",
    
    DOMAIN_NAME="dev-pecha-esukhai.us.auth0.com",
    CLIENT_ID="", 
)


def get(key: str) -> str:
    if key in os.environ:
        return os.environ[key]
    else:
        return str(DEFAULTS[key])


def get_float(key: str) -> float:
    try:
        return float(get(key))
    except (TypeError, ValueError) as e:
        raise ValueError(f"Could not convert the value for key '{key}' to float: {e}")


def get_int(key: str) -> int:
    try:
        return int(get(key))
    except (TypeError, ValueError) as e:
        raise ValueError(f"Could not convert the value for key '{key}' to int: {e}")
