import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from app.connection.base_class import Base

class UserModel(Base):
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    nome = Column(String, index=True, nullable=False)
    username = Column(String, index=True, nullable=True)
    cpf = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    telefone = Column(String, nullable=True)
    ativo = Column(Boolean, default=True)
    hashed_senha = Column(String)
    endereco_id = Column(UUID(as_uuid=True), ForeignKey("enderecos.id"), nullable=True)
    token = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(UUID(as_uuid=True), index=True, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(UUID(as_uuid=True), index=True, nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(UUID(as_uuid=True), index=True, nullable=True)

    endereco = relationship("EnderecoModel", back_populates="usuario")
    log = relationship("LogModel", back_populates="usuario")