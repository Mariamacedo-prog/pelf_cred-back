from pydantic import BaseModel
from app.schemas.User import UserBase


class LoginRequest(BaseModel):
    login: str
    senha: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str