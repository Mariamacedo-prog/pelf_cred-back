import uuid
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
from sqlalchemy import Column, String, Boolean, DateTime, Text, Numeric, Integer
from app.connection.base_class import Base

class ServicoModel(Base):
    __tablename__ = "servicos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    nome = Column(String, unique=True, index=True, nullable=False)
    descricao = Column(Text, index=True, nullable=True)
    ativo = Column(Boolean, default=True)
    valor = Column(Numeric(10, 2), index=True, nullable=False)
    categoria = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(UUID(as_uuid=True), index=True, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(UUID(as_uuid=True), index=True, nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(UUID(as_uuid=True), index=True, nullable=True)