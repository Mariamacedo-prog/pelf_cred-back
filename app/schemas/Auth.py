from pydantic import BaseModel
from app.schemas.User import UserBase


class LoginRequest(BaseModel):
    doc: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str