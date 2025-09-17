import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.connection.base_class import Base

class Log(Base):
    __tablename__ = "log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tabela_afetada = Column(String, index=True, nullable=False)
    operacao = Column(String, index=True, nullable=True)
    registro_id = Column(UUID(as_uuid=True), index=True, nullable=True)
    dados_antes = Column(JSONB, nullable=True)
    dados_depois = Column(JSONB, nullable=True)
    usuario_id = Column(UUID(as_uuid=True), index=True, nullable=True)
    data_hora = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)