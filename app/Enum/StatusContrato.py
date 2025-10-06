from enum import Enum

class StatusContrato(str, Enum):
    PENDENTE_ASSINATURA = "PENDENTE_ASSINATURA"
    ATIVO = "ATIVO"
    INICIADO = "INICIADO"
    CANCELADO = "CANCELADO"
    EXPIRADO = "EXPIRADO"