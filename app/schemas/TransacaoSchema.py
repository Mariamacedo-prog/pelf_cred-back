from datetime import datetime

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID, uuid4

from app.schemas.AnexoSchema import AnexoRequest


class TransacaoResponse(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    contrato_id: Optional[UUID] = None
    plano_id: Optional[UUID] = None
    comprovante_numero: Optional[str] = None
    status_parcela: Optional[str] = None
    meio_pagamento: Optional[str] = None
    status_comprovante: Optional[str] = None
    data_vencimento: Optional[datetime] = None
    data_pagamento: Optional[datetime] = None
    anexo_id: Optional[UUID] = None
    valor: Optional[float] = None
    valor_pago: Optional[float] = None
    numero_parcela: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    deleted_by: Optional[UUID] = None


class TransacaoUpdate(BaseModel):
    comprovante_numero: Optional[str] = None
    status_parcela: Optional[str] = None
    meio_pagamento: Optional[str] = None
    status_comprovante: Optional[str] = None
    data_pagamento: Optional[datetime] = None
    anexo: Optional[AnexoRequest] = None
    valor_pago: Optional[float] = None


class PaginatedTransacaoResponse(BaseModel):
    total_items: int
    total_paginas: int
    pagina_atual: int
    items: int
    offset: int
    data: List[TransacaoResponse]


class TransacaoTotais(BaseModel):
    total_pago: Optional[float] = None
    total_gerado: Optional[float] = None
    total_em_atraso: Optional[float] = None
    total_cancelado: Optional[float] = None