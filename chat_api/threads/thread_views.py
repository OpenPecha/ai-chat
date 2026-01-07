from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from uuid import UUID
from starlette import status
from typing import Annotated

from chat_api.threads import thread_service
from chat_api.threads.thread_response_model import ThreadResponse, ThreadListResponse
from chat_api.auth_utils import get_user_email_from_token

oauth2_scheme = HTTPBearer()

thread_router = APIRouter(
    prefix="/threads",
    tags=["Threads"]
)


@thread_router.get("", status_code=status.HTTP_200_OK, response_model=ThreadListResponse)
async def get_threads(
    authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
    email: str,
    application: str,
    skip: int = 0,
    limit: int = 10
):
    try:
        get_user_email_from_token(authentication_credential.credentials)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    
    return await thread_service.get_all_threads(
        email=email,
        application=application,
        skip=skip,
        limit=limit
    )


@thread_router.get("/{thread_id}", status_code=status.HTTP_200_OK, response_model=ThreadResponse)
async def get_thread_details(
    thread_id: UUID,
    authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)]
):
    try:
        get_user_email_from_token(authentication_credential.credentials)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    
    return await thread_service.get_thread_by_id(thread_id)


@thread_router.delete("/{thread_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_thread(
    thread_id: UUID,
    authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)]
):
    try:
        get_user_email_from_token(authentication_credential.credentials)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    
    await thread_service.delete_thread_by_id(thread_id)
    return None
