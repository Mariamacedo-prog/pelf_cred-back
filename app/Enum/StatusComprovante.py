from enum import Enum

class StatusComprovante(str, Enum):
    EM_ANALISE = "EM_ANALISE"
    AGUARDANDO = "AGUARDANDO"
    ACEITO = "ACEITO"
    NEGADO = "NEGADO"