from enum import Enum

class TipoPagamento(str, Enum):
    MENSAL = "MENSAL"
    SEMANAL = "SEMANAL"