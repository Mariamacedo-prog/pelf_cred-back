from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    id:int
    username: str
    doc: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    token: str

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    hashed_password: str

class UserOut(BaseModel):
    id: int
    username: str
    doc: str
    email: Optional[EmailStr]

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None