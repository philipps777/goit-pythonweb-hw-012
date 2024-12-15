from fastapi import APIRouter

router = APIRouter(prefix="/healthcheck", tags=["healthcheck"])

@router.get("/")
async def healthcheck():
    """
    Endpoint API healthcheck
    """
    return {"status": "ok", "message": "API is working"}
