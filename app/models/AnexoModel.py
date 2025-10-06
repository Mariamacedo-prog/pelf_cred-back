import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Column, String, DateTime, Text, LargeBinary
from app.connection.base_class import Base

class AnexoModel(Base):
    __tablename__ = "anexos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    base64 = Column(LargeBinary, nullable=True)
    image = Column(String, index=True, nullable=True)
    nome = Column(String, index=True, nullable=True)
    tipo = Column(String, index=True, nullable=True)
    responsavel = Column(String, index=True, nullable=True)
    descricao = Column(Text, index=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(UUID(as_uuid=True), index=True, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(UUID(as_uuid=True), index=True, nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(UUID(as_uuid=True), index=True, nullable=True)

    vendedor = relationship("VendedorModel", back_populates="foto")
    contratos_como_cliente = relationship("ContratoModel",foreign_keys="[ContratoModel.cliente_assinatura_id]", back_populates="cliente_assinatura")
    contratos_como_responsavel = relationship("ContratoModel",foreign_keys="[ContratoModel.responsavel_assinatura_id]",back_populates="responsavel_assinatura")