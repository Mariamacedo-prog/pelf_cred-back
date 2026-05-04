from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime

from app.schemas.ContratoSchema import ContratoResponse


class ContatoBase(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    meio:Optional[str]
    contrato_id: Optional[UUID] = None
    usuario_id: Optional[UUID] = None
    cliente_id: Optional[UUID] = None
    data_hora: Optional[datetime] = None
    valor: Optional[float]
    descricao: Optional[str]
    status: Optional[str]
    created_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    efetivo: Optional[bool] = None

class ContatoRequest(BaseModel):
    id: UUID | None = None
    meio: Optional[str]
    contrato_id: Optional[UUID] = None
    cliente_id: Optional[UUID] = None
    data_hora: Optional[datetime] = None
    valor: Optional[float]
    descricao: Optional[str]
    status: Optional[str]
    created_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    efetivo: Optional[bool] = None

class ContatoResponse(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    meio: Optional[str]
    contrato_id: Optional[UUID] = None
    usuario_id: Optional[UUID] = None
    cliente_id: Optional[UUID] = None
    data_hora: Optional[datetime] = None
    valor: Optional[float]
    descricao: Optional[str]
    status: Optional[str]
    created_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    efetivo: Optional[bool] = None


class PaginatedContatosResponse(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    contrato: ContratoResponse
    total_items: int
    total_paginas: int
    pagina_atual: int
    items: int
    offset: int
    data: List[ContatoResponse]
