import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


def limpar_dict_para_json(obj):
    result = {}

    if isinstance(obj, BaseModel):
        obj = obj.dict()
    elif hasattr(obj, "__dict__"):
        obj = obj.__dict__

    for key, value in obj.items():
        if key == "_sa_instance_state":
            continue

        if isinstance(value, uuid.UUID):
            result[key] = str(value)

        elif isinstance(value, datetime):
            result[key] = value.isoformat()

        elif isinstance(value, Decimal):
            result[key] = float(value)

        elif isinstance(value, BaseModel):
            result[key] = limpar_dict_para_json(value)

        elif isinstance(value, dict):
            result[key] = limpar_dict_para_json(value)

        elif isinstance(value, list):
            result[key] = [limpar_dict_para_json(item) if isinstance(item, (dict, BaseModel)) else item for item in value]

        else:
            result[key] = value

    return result