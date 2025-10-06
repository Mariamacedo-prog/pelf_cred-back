import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Numeric, Integer
from app.connection.base_class import Base

class ParcelamentoModel(Base):
    __tablename__ = "parcelamentos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    contrato_id = Column(UUID(as_uuid=True), nullable=True)
    data_inicio = Column(DateTime(timezone=True), nullable=True)
    data_fim = Column(DateTime(timezone=True), nullable=True)
    data_vigencia = Column(DateTime(timezone=True), nullable=True)
    meio_pagamento = Column(String, index=True, nullable=True)
    valor_total = Column(Numeric(10, 2), index=True, nullable=False)
    valor_parcela = Column(Numeric(10, 2), index=True, nullable=False)
    valor_entrada = Column(Numeric(10, 2), index=True, nullable=True)
    qtd_parcela = Column(Integer, index=True, nullable=False)
    avista = Column(Boolean, index=True, nullable=True)
    taxa_juros = Column(Numeric(10, 2), index=True, nullable=True)
    data_ultimo_pagamento = Column(DateTime(timezone=True), nullable=True)
    qtd_parcelas_pagas = Column(Integer, index=True, nullable=True)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(UUID(as_uuid=True), index=True, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(UUID(as_uuid=True), index=True, nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(UUID(as_uuid=True), index=True, nullable=True)

    contrato = relationship("ContratoModel", back_populates="parcelamento",foreign_keys="[ContratoModel.parcelamento_id]")