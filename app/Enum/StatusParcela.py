from enum import Enum

class StatusParcela(str, Enum):
    PAGA = "PAGA"
    EM_PAGAMENTO = "EM_PAGAMENTO"
    EM_ANALISE = "EM_ANALISE"
    EM_ATRASO = "EM_ATRASO"
    CANCELADO = "CANCELADO"
    GERADO = "GERADO"