import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import Numeric, Boolean, Text

from app.connection.base_class import Base

class ContatoModel(Base):
    __tablename__ = "contato"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    meio = Column(String, index=True, nullable=True)
    contrato_id = Column(UUID(as_uuid=True), index=True, nullable=True)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    cliente_id = Column(UUID(as_uuid=True), index=True, nullable=True)
    data_hora = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    valor = Column(Numeric(10, 2), index=True, nullable=True)
    efetivo = Column(Boolean, default=False)
    descricao = Column(Text, index=True, nullable=True)
    status = Column(String, index=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(UUID(as_uuid=True), index=True, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(UUID(as_uuid=True), index=True, nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(UUID(as_uuid=True), index=True, nullable=True)