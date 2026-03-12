from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime


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