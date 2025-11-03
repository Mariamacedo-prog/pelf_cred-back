import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

def limpar_dict_para_json(obj):
    # Se for UUID, retorna string
    if isinstance(obj, uuid.UUID):
        return str(obj)

    # Se for datetime, retorna isoformat
    if isinstance(obj, datetime):
        return obj.isoformat()

    # Se for Decimal, converte para float
    if isinstance(obj, Decimal):
        return float(obj)

    # Se for bytes, pula (ignora campos binários)
    if isinstance(obj, bytes):
        return None  # Ou simplesmente não adiciona ao resultado

    # Se for lista, processa cada item
    if isinstance(obj, list):
        return [limpar_dict_para_json(item) for item in obj]

    # Se for BaseModel do Pydantic, transforma em dict
    if isinstance(obj, BaseModel):
        obj = obj.dict()

    # Se for objeto com __dict__, pega o dict
    elif hasattr(obj, "__dict__"):
        obj = obj.__dict__

    # Se for dict, processa as chaves e valores
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            if key == "_sa_instance_state":
                continue
            if isinstance(value, bytes):  # Ignora campos binários
                continue
            result[key] = limpar_dict_para_json(value)
        return result

    # Se chegou aqui, é um valor simples: retorna direto
    return obj
