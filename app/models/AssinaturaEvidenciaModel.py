import uuid
from sqlalchemy import Column, String, DateTime, Text, JSON, VARCHAR, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.connection.base_class import Base

class AssinaturaEvidenciaModel(Base):
    __tablename__ = "assinatura_evidencia"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    contrato_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    anexo_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    email_responsavel = Column(String, index=True, nullable=True)
    nome_responsavel = Column(String, index=True, nullable=True)
    documento_responsavel = Column(String, index=True, nullable=True)
    geolocalizacao = Column(String, index=True, nullable=True)
    # 1 - cliente vai clicar em botão assinar
    # 2 - cliente vai receber email com codigo_verificacao
    # 3 - digitou o codigo de verificação clica em confirmar
    # 4 - aparece pop up, com termo pra autorizar guardar dados etc, ip:
    # 5 - CLIENTE ACEITA TERMO => é enviado por email um link unico, pra abrir precisa digitar o email e o documento,
    # com pop up com a visualização do contrato e o botão no final escrito assinar, lembrando que esse processo é irreversível.
    # 6 - CLIENTE NÃO ACEITA TERMO =>  é enviado por email um link unico,  pra abrir precisa digitar o email e o documento,
    # com pop up solicita o pdf do contrato assinado, manualmente ou por via .gov
    # e o botão no final escrito assinar, lembrando que esse processo é irreversível, no final fala que a assinatura vai para análise.

    codigo_verificacao = Column(String, nullable=True)
    tentativas_codigo = Column(Integer, nullable=False, default=0)
    codigo_validado_em = Column(DateTime(timezone=True), nullable=True)
    evento = Column(String, nullable=False, index=True)  # ex: 'assinou', 'clicou'
    status_assinatura = Column(String, nullable=True, index=True)  # ex: 'pendente', 'assinada'

    metodo_autenticacao = Column(String, nullable=True)

    token = Column(String, nullable=True)
    documento_hash = Column(String, nullable=True)

    ip = Column(VARCHAR(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    headers = Column(JSON, nullable=True)
    extras = Column(JSON, nullable=True)

    timestamp_utc = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    evidence_hmac = Column(String, nullable=True)
