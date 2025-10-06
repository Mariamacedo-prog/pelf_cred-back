from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime

class ParcelamentoBase(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    contrato_id: Optional[UUID] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    data_vigencia: Optional[datetime] = None
    meio_pagamento: Optional[str] = None
    valor_total: float
    valor_parcela: float
    valor_entrada: Optional[float] = None
    qtd_parcela: int
    avista: Optional[bool] = None
    taxa_juros: Optional[float] = None
    data_ultimo_pagamento: Optional[datetime] = None
    qtd_parcelas_pagas: Optional[int] = None
    ativo: Optional[bool] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    deleted_by: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None


class ParcelamentoRequest(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    contrato_id: Optional[UUID] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    data_vigencia: Optional[datetime] = None
    meio_pagamento: Optional[str] = None
    valor_total: Optional[float] = None
    valor_parcela:  Optional[float] = None
    valor_entrada: Optional[float] = None
    qtd_parcela: Optional[int] = None
    avista: Optional[bool] = None
    taxa_juros: Optional[float] = None
    data_ultimo_pagamento: Optional[datetime] = None
    qtd_parcelas_pagas: Optional[int] = None
    ativo: Optional[bool] = None


class ParcelamentoResponse(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    contrato_id: Optional[UUID] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    data_vigencia: Optional[datetime] = None
    meio_pagamento: Optional[str] = None
    valor_total: float
    valor_parcela: float
    valor_entrada: Optional[float] = None
    qtd_parcela: int
    avista: Optional[bool] = None
    taxa_juros: Optional[float] = None
    data_ultimo_pagamento: Optional[datetime] = None
    qtd_parcelas_pagas: Optional[int] = None
    ativo: Optional[bool] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    deleted_by: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None


class PaginateParcelamentoResponse(BaseModel):
    total_items: int
    total_paginas: int
    pagina_atual: int
    items: int
    offset: int
    data: List[ParcelamentoResponse]


class ParcelamentoUpdate(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    data_vigencia: Optional[datetime] = None
    meio_pagamento: Optional[str] = None
    valor_total: Optional[float] = None
    valor_parcela: Optional[float] = None
    valor_entrada: Optional[float] = None
    qtd_parcela: Optional[int] = None
    avista: Optional[bool] = None
    taxa_juros: Optional[float] = None
    data_ultimo_pagamento: Optional[datetime] = None
    qtd_parcelas_pagas: Optional[int] = None
    ativo: Optional[bool] = None
