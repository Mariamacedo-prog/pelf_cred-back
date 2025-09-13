from fastapi import APIRouter

router = APIRouter()

@router.get("/", tags=["Root"])
async def root():
    return {"message": "Hello World"}