from pydantic import BaseModel

class ErrorConstants:
    MAX_QUERY_LENGTH_ERROR = "Query cannot exceed 2000 characters"
    BAD_REQUEST = "Bad Request"
    UNAUTHORIZED = "Unauthorized"

class ResponseError(BaseModel):
    error: str
    message: str