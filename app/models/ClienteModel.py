import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.connection.base_class import Base

class ClienteModel(Base):
    __tablename__ = "clientes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    endereco_id = Column(UUID(as_uuid=True), ForeignKey("enderecos.id"), nullable=True)
    nome = Column(String, index=True, nullable=False)
    documento = Column(String, index=True, nullable=False)
    telefone = Column(String, index=True, nullable=False)
    email = Column(String, index=True, nullable=False)
    grupo_segmento = Column(String, index=True, nullable=True)
    disabled = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(UUID(as_uuid=True), index=True, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(UUID(as_uuid=True), index=True, nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(UUID(as_uuid=True), index=True, nullable=True)

    endereco = relationship("Endereco", back_populates="cliente")