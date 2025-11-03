from enum import Enum

class StatusParcela(str, Enum):
    PAGA = "PAGA"
    EM_ATRASO = "EM ATRASO"
    CANCELADO = "CANCELADO"
    GERADO = "GERADO"