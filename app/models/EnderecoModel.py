import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Column, String, DateTime
from app.connection.base_class import Base

class EnderecoModel(Base):
    __tablename__ = "enderecos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    cep = Column(String, index=True, nullable=False)
    rua = Column(String, index=True, nullable=True)
    numero = Column(String, index=True, nullable=True)
    bairro = Column(String, index=True, nullable=True)
    complemento = Column(String, index=True, nullable=True)
    cidade = Column(String, index=True, nullable=True)
    uf = Column(String, index=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(UUID(as_uuid=True), index=True, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(UUID(as_uuid=True), index=True, nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(UUID(as_uuid=True), index=True, nullable=True)

    usuario = relationship("UserModel", back_populates="endereco")
    cliente = relationship("ClienteModel", back_populates="endereco")