from fastapi import APIRouter

router = APIRouter()

@router.get("/", tags=["Root"])
async def root():
    return {"message": "Hello World"}

@router.get("/hello/{name}", tags=["Root"])
async def say_hello(name: str):
    return {"message": f"Hello {name}"}