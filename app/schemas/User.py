from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

from app.schemas.Endereco import EnderecoRequest


class UserBase(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    username: Optional[str]  = None
    nome: str
    cpf: str
    email: EmailStr
    telefone: Optional[str] = None
    disabled: Optional[bool] = None
    endereco_id:  Optional[UUID] = None
    token: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None


class UserRequest(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    username: Optional[str]  = None
    nome: str
    cpf: str
    senha: str
    email: EmailStr
    telefone: Optional[str] = None
    endereco: EnderecoRequest

class UserResponse(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    username: Optional[str]  = None
    nome: str
    cpf: str
    email: EmailStr
    telefone: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    endereco: EnderecoRequest = None


class UserCreate(UserBase):
    senha: str

class UserInDB(UserBase):
    hashed_senha: str

class UserOut(BaseModel):
    id: int
    nome: str
    cpf: str
    email: EmailStr

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str