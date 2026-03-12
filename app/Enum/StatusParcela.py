from enum import Enum

class StatusParcela(str, Enum):
    PAGA = "PAGA"
    PAGAMENTO_PARCIAL = "PAGAMENTO_PARCIAL"
    EM_ANALISE = "EM_ANALISE"
    EM_ATRASO = "EM_ATRASO"
    CANCELADO = "CANCELADO"
    GERADO = "GERADO"