import logging
from typing import Dict, Any

from jose import jwt, JWTError
import requests

from chat_api.config import get


def validate_token(token: str) -> Dict[str, Any]:

    if get("DOMAIN_NAME") in jwt.get_unverified_claims(token=token)["iss"]:
        return verify_auth0_token(token)
    else:
        return decode_backend_token(token)


def decode_backend_token(token: str) -> Dict[str, Any]:
    claims = jwt.get_unverified_claims(token)
    logging.info(f"Token audience: {claims.get('aud')}, Expected: {get('JWT_AUD')}")
    
    return jwt.decode(
        token, 
        get("JWT_SECRET_KEY"), 
        algorithms=[get("JWT_ALGORITHM")], 
        audience=get("JWT_AUD")
    )


def get_auth0_public_key():

    jwks_url = f"https://{get('DOMAIN_NAME')}/.well-known/jwks.json"
    jwks = requests.get(jwks_url).json()
    return {key["kid"]: key for key in jwks["keys"]}


def verify_auth0_token(token: str) -> Dict[str, Any]:

    try:
        jwks = get_auth0_public_key()
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = jwks.get(unverified_header["kid"])

        if not rsa_key:
            raise ValueError("Unable to find appropriate key")

        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience=get("CLIENT_ID"),
            issuer=f"https://{get('DOMAIN_NAME')}/"
        )
        return payload
    except JWTError as e:
        raise ValueError(f"Token validation failed: {e}")


def get_user_email_from_token(token: str) -> str:

    try:
        payload = validate_token(token)
        email = payload.get("email")
        if email is None:
            raise ValueError("Email not found in token")
        return email
    except Exception as e:
        logging.error(f"Error extracting email from token: {e}")
        raise ValueError(f"Invalid token: {e}")
