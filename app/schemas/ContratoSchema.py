from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime

from app.schemas.AnexoSchema import AnexoRequest
from app.schemas.ClienteSchema import  ClienteContratoResponse
from app.schemas.ParcelamentoSchema import ParcelamentoRequest, ParcelamentoResponse, ParcelamentoUpdate
from app.schemas.VendedorSchema import  VendedorContratoResponse


class ContratoBase(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    numero: Optional[int] = None
    parcelamento_id: Optional[UUID] = None
    cliente_id: Optional[UUID] = None
    vendedor_id: Optional[UUID] = None
    cliente_assinatura_id: Optional[UUID] = None
    responsavel_assinatura_id: Optional[UUID] = None
    nome: Optional[str] = None
    documento: Optional[str] = None
    status_cobranca: Optional[str] = None
    status_contrato: Optional[str] = None
    anexos_list_id: Optional[List[UUID]] = None
    ativo: Optional[bool] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    deleted_by: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    


class ContratoRequest(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    numero: Optional[int] = None
    cliente_id: Optional[UUID] = None
    vendedor_id: Optional[UUID] = None
    nome: Optional[str] = None
    documento: Optional[str] = None
    status_cobranca: Optional[str] = None
    status_contrato: Optional[str] = None
    ativo: Optional[bool] = None
    parcelamento: Optional[ParcelamentoRequest] = None
    cliente_assinatura: Optional[AnexoRequest] = None
    responsavel_assinatura: Optional[AnexoRequest] = None
    anexos_list: Optional[List[AnexoRequest]] = None





class ContratoResponse(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    numero: Optional[int] = None
    cliente: Optional[ClienteContratoResponse] = None
    vendedor: Optional[VendedorContratoResponse] = None
    nome: Optional[str] = None
    documento: Optional[str] = None
    status_cobranca: Optional[str] = None
    status_contrato: Optional[str] = None
    ativo: Optional[bool] = None
    parcelamento: Optional[ParcelamentoResponse] = None
    cliente_assinatura: Optional[AnexoRequest] = None
    responsavel_assinatura: Optional[AnexoRequest] = None
    anexos_list: Optional[List[AnexoRequest]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    deleted_by: Optional[UUID] = None


class ContratoResponseShort(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    numero: Optional[int] = None
    cliente: Optional[ClienteContratoResponse] = None
    status_cobranca: Optional[str] = None
    status_contrato: Optional[str] = None
    ativo: Optional[bool] = None
    parcelamento: Optional[ParcelamentoResponse] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PaginateContratoResponse(BaseModel):
    total_items: int
    total_paginas: int
    pagina_atual: int
    items: int
    offset: int
    data: List[ContratoResponseShort]


class ContratoUpdate(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    cliente_id: Optional[UUID] = None
    vendedor_id: Optional[UUID] = None
    parcelamento: Optional[ParcelamentoUpdate] = None
    cliente_assinatura: Optional[AnexoRequest] = None
    responsavel_assinatura: Optional[AnexoRequest] = None
    anexos_list: Optional[List[AnexoRequest]] = None
    ativo: Optional[bool] = None