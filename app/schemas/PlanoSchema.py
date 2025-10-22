from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime

from app.schemas.EnderecoSchema import EnderecoRequest, EnderecoUpdate
from app.schemas.ServicoSchema import ServicoList


class PlanoBase(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    nome: str
    descricao: Optional[str] = None
    valor_mensal: float
    valor_total: Optional[float] = None
    numero_parcelas: Optional[int] = None
    ativo: bool
    avista: Optional[bool] = None
    periodo_vigencia: Optional[str] = None
    servicos_vinculados:  Optional[List[UUID]] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    deleted_by: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None


class PlanoRequest(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    nome: str
    descricao: Optional[str] = None
    valor_mensal: float
    numero_parcelas: Optional[int] = None
    avista: Optional[bool] = None
    periodo_vigencia: Optional[str] = None
    servicos_vinculados: Optional[List[UUID]] = None



class PlanoServicoResponse(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    nome: str
    descricao: Optional[str] = None
    valor_mensal: float
    valor_total: Optional[float] = None
    numero_parcelas: Optional[int] = None
    ativo: bool
    avista: Optional[bool] = None
    periodo_vigencia: Optional[str] = None
    servicos_vinculados:  Optional[List[ServicoList]] = None


class PlanoUpdate(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    nome: Optional[str] = None
    descricao: Optional[str] = None
    valor_mensal: Optional[float] = None
    valor_total: Optional[float] = None
    numero_parcelas: Optional[int] = None
    ativo: Optional[bool] = None
    avista: Optional[bool] = None
    periodo_vigencia: Optional[str] = None
    servicos_vinculados: List[UUID] = None


class PaginatedPlanoResponse(BaseModel):
        total_items: int
        total_paginas: int
        pagina_atual: int
        items: int
        offset: int
        data: List[PlanoServicoResponse]