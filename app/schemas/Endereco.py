from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime


class EnderecoBase(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    cep: str
    rua: Optional[str]
    numero: Optional[str]
    bairro: Optional[str]
    complemento: Optional[str]
    cidade: Optional[str]
    uf: Optional[str]

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None


class EnderecoRequest(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    cep: str
    rua: Optional[str]
    numero: Optional[str]
    bairro: Optional[str]
    complemento: Optional[str]
    cidade: Optional[str]
    uf: Optional[str]
