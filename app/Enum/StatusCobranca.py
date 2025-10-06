from enum import Enum

class StatusCobranca(str, Enum):
    NAO_INICIADA = "NAO_INICIADA"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    EM_DIA = "EM_DIA"
    ATRASADA = "ATRASADA"
    CANCELADA = "CANCELADA"
    CONCLUIDA = "CONCLUIDA"