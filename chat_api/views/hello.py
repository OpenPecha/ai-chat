from fastapi import APIRouter

router = APIRouter()


@router.get("/", tags=["hello"])
async def hello() -> dict[str, str]:
    return {"message": "Hello, world!"}


@router.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


