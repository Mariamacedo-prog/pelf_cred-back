from pydantic import BaseModel


class LoginRequest(BaseModel):
    login: str
    senha: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str