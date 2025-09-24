import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from app.connection.base_class import Base

class VendedorModel(Base):
    __tablename__ = "vendedores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    nome = Column(String, index=True, nullable=False)
    cpf = Column(String, index=True, nullable=False)
    rg = Column(String, index=True, nullable=True)
    endereco_id = Column(UUID(as_uuid=True), ForeignKey("enderecos.id"), nullable=True)
    telefone = Column(String, index=True, nullable=False)
    email = Column(String, index=True, nullable=False)
    foto_id = Column(UUID(as_uuid=True), ForeignKey("anexos.id"), nullable=True)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(UUID(as_uuid=True), index=True, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(UUID(as_uuid=True), index=True, nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(UUID(as_uuid=True), index=True, nullable=True)

    endereco = relationship("EnderecoModel", back_populates="vendedor")
    foto = relationship("AnexoModel", back_populates="vendedor")