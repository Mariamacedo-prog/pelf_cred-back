import uuid
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Column, String, Boolean, DateTime, Text, Numeric, Integer
from app.connection.base_class import Base

class PlanoModel(Base):
    __tablename__ = "planos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    nome = Column(String, unique=True, index=True, nullable=False)
    descricao = Column(Text, index=True, nullable=True)
    valor_mensal = Column(Numeric(10, 2), index=True, nullable=True)
    valor_total = Column(Numeric(10, 2), index=True, nullable=True)
    numero_parcelas = Column(Integer, index=True, nullable=True)
    entrada = Column(Numeric(10, 2), index=True, nullable=True)
    ativo = Column(Boolean, default=True)
    avista = Column(Boolean, default=None)
    periodo_vigencia = Column(String, nullable=True)
    servicos_vinculados = Column(ARRAY(UUID(as_uuid=True)), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(UUID(as_uuid=True), index=True, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(UUID(as_uuid=True), index=True, nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(UUID(as_uuid=True), index=True, nullable=True)

    contrato = relationship("ContratoModel", back_populates="plano")