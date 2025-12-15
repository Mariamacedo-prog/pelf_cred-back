import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy import Column, String, DateTime, Numeric, Integer
from app.connection.base_class import Base

class TransacaoModel(Base):
    __tablename__ = "transacoes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    contrato_id = Column(UUID(as_uuid=True), nullable=False)
    plano_id = Column(UUID(as_uuid=True), nullable=True)
    valor = Column(Numeric(10, 2), index=True, nullable=True)
    valor_pago = Column(Numeric(10, 2), index=True, default=0)
    numero_parcela = Column(Integer, index=True, nullable=True)
    numero_contrato = Column(Integer, index=True, nullable=True)
    status_parcela = Column(String, index=True, nullable=True)
    comprovante_numero = Column(String, index=True, nullable=True)
    data_vencimento = Column(DateTime(timezone=True), index=True, nullable=True)
    data_pagamento = Column(DateTime(timezone=True), index=True, nullable=True)
    meio_pagamento = Column(String, index=True, nullable=True)
    anexo_id = Column(UUID(as_uuid=True), nullable=True)
    status_comprovante = Column(String, index=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(UUID(as_uuid=True), index=True, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(UUID(as_uuid=True), index=True, nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(UUID(as_uuid=True), index=True, nullable=True)