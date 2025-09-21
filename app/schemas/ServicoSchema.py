from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime

from app.schemas.EnderecoSchema import EnderecoRequest, EnderecoUpdate


class ServicoBase(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    nome: str
    descricao: Optional[str] = None
    ativo: bool
    valor: float
    categoria: Optional[str] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    deleted_by: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None


class ServicoRequest(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    nome: str
    descricao: Optional[str] = None
    valor: float
    categoria: Optional[str] = None


class ServicoList(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    nome: str
    valor: float
    categoria: Optional[str] = None


class PaginatedServicoResponse(BaseModel):
    total_items: int
    total_paginas: int
    pagina_atual: int
    items: int
    offset: int
    data: List[ServicoBase]

class PaginatedServicoListResponse(BaseModel):
    total_items: int
    total_paginas: int
    pagina_atual: int
    items: int
    offset: int
    data: List[ServicoList]


class ServicoUpdate(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    nome: Optional[str] = None
    descricao: Optional[str] = None
    valor: Optional[float] = None
    categoria: Optional[str] = None
    ativo: Optional[bool] = None
