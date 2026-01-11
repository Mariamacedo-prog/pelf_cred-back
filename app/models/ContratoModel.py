import uuid
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Integer, Sequence
from app.connection.base_class import Base

class ContratoModel(Base):
    __tablename__ = "contratos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    numero = Column(
        Integer,
        Sequence('numero_contrato_seq', start=1, increment=1),
        index=True,
        nullable=False,
        unique=True
    )
    parcelamento_id = Column(UUID(as_uuid=True), ForeignKey("parcelamentos.id"), nullable=True)
    cliente_assinatura_id = Column(UUID(as_uuid=True), ForeignKey("anexos.id"), nullable=True)
    responsavel_assinatura_id = Column(UUID(as_uuid=True), ForeignKey("anexos.id"), nullable=True)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=True)
    vendedor_id = Column(UUID(as_uuid=True), ForeignKey("vendedores.id"), nullable=True)
    anexos_list_id = Column(ARRAY(UUID(as_uuid=True)), nullable=True)
    nome = Column(String, index=True, nullable=False)
    documento = Column(String, index=True, nullable=False)
    status_cobranca = Column(String, index=True, nullable=True)
    status_contrato = Column(String, index=True, nullable=True)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(UUID(as_uuid=True), index=True, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(UUID(as_uuid=True), index=True, nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(UUID(as_uuid=True), index=True, nullable=True)

    parcelamento = relationship("ParcelamentoModel",foreign_keys=[parcelamento_id], back_populates="contrato")
    cliente_assinatura = relationship( "AnexoModel",foreign_keys=[cliente_assinatura_id],back_populates="contratos_como_cliente")
    responsavel_assinatura = relationship("AnexoModel",foreign_keys=[responsavel_assinatura_id], back_populates="contratos_como_responsavel")
    cliente = relationship("ClienteModel", back_populates="contrato")
    vendedor = relationship("VendedorModel", back_populates="contrato")