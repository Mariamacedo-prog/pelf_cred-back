from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime

from app.schemas.EnderecoSchema import EnderecoRequest, EnderecoUpdate


class UserBase(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    username: Optional[str]  = None
    nome: str
    cpf: str
    email: EmailStr
    telefone: Optional[str] = None
    ativo: Optional[bool] = None
    endereco_id: Optional[UUID] = None
    token: Optional[str] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    deleted_by: Optional[UUID] = None
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
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    deleted_by: Optional[UUID] = None
    endereco: EnderecoRequest = None

class PaginatedUserResponse(BaseModel):
    total_items: int
    total_paginas: int
    pagina_atual: int
    items: int
    offset: int
    data: List[UserResponse]

class UserInDB(UserBase):
    hashed_senha: str

class UserUpdate(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    username: Optional[str]  = None
    nome: Optional[str] = None
    cpf: Optional[str] = None
    email: Optional[str] = None
    senha: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[EnderecoUpdate] = None