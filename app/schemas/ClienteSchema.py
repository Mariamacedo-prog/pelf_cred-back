from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime

from app.schemas.EnderecoSchema import EnderecoRequest, EnderecoUpdate


class ClienteBase(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    endereco_id: Optional[UUID] = None
    endereco_comercial_id: Optional[UUID] = None
    nome: str
    documento: str
    email: EmailStr
    telefone: Optional[str] = None
    grupo_segmento:  Optional[str] = None
    ativo: Optional[bool] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    deleted_by: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None


class ClienteRequest(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    nome: str
    documento: str
    email: EmailStr
    telefone: Optional[str] = None
    grupo_segmento: Optional[str] = None
    endereco: EnderecoRequest
    endereco_comercial: Optional[EnderecoRequest] = None


class ClienteResponse(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    nome: str
    documento: str
    email: EmailStr
    telefone: Optional[str] = None
    grupo_segmento: Optional[str] = None
    endereco_comercial: Optional[EnderecoRequest] = None
    endereco: EnderecoRequest = None
    ativo: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    deleted_by: Optional[UUID] = None


class ClienteContratoResponse(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    nome: str
    documento: str
    email: EmailStr
    telefone: Optional[str] = None
    grupo_segmento: Optional[str] = None
    endereco_comercial: Optional[EnderecoRequest] = None
    endereco: EnderecoRequest = None
    ativo: Optional[bool] = None


class PaginatedClienteResponse(BaseModel):
    total_items: int
    total_paginas: int
    pagina_atual: int
    items: int
    offset: int
    data: List[ClienteResponse]


class ClienteUpdate(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    documento: Optional[str]  = None
    nome: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None
    grupo_segmento: Optional[str] = None
    endereco_comercial: Optional[EnderecoUpdate] = None
    endereco: Optional[EnderecoUpdate] = None