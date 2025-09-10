from fastapi import APIRouter

router = APIRouter()

@router.get("/api/v1/", tags=["Root"])
async def root():
    return {"message": "Hello World"}

@router.get("/api/v1/hello/{name}", tags=["Root"])
async def say_hello(name: str):
    return {"message": f"Hello {name}"}