from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime

from app.schemas.AnexoSchema import AnexoRequest
from app.schemas.EnderecoSchema import EnderecoRequest, EnderecoUpdate


class VendedorBase(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    nome: str
    cpf: str
    email: EmailStr
    telefone: str
    rg: Optional[str] = None
    ativo: Optional[bool] = None
    endereco_id: Optional[UUID] = None
    foto_id: Optional[UUID] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    deleted_by: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None


class VendedorRequest(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    nome: str
    cpf: str
    email: EmailStr
    telefone: str
    rg: Optional[str] = None
    ativo: Optional[bool] = None
    foto: Optional[AnexoRequest] = None
    endereco: EnderecoRequest

class VendedorResponse(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    nome: str
    cpf: str
    email: EmailStr
    telefone: str
    rg: Optional[str] = None
    ativo: Optional[bool] = None
    foto: Optional[AnexoRequest] = None
    endereco: EnderecoRequest
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    deleted_by: Optional[UUID] = None

class PaginatedVendedorResponse(BaseModel):
    total_items: int
    total_paginas: int
    pagina_atual: int
    items: int
    offset: int
    data: List[VendedorResponse]


class VendedorUpdate(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    nome: Optional[str]  = None
    cpf: Optional[str]  = None
    email: Optional[EmailStr]  = None
    telefone: Optional[str]  = None
    rg: Optional[str]  = None
    foto: Optional[AnexoRequest] = None
    endereco: Optional[EnderecoUpdate] = None