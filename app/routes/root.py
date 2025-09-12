from fastapi import APIRouter

router = APIRouter()

@router.get("/api/v1/", tags=["Root"])
async def root():
    return {"message": "Hello World"}