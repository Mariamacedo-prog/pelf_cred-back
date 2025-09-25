import base64


def base64_to_bytes(data_url: str) -> bytes:
    if ',' in data_url:
        # Remove o prefixo data:image/jpeg;base64,
        header, base64_str = data_url.split(',', 1)
    else:
        base64_str = data_url
    try:
        return base64.b64decode(base64_str)
    except Exception as e:
        raise ValueError("Base64 inválido") from e


def bytes_to_base64(data_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    if not data_bytes:
        return None
    base64_str = base64.b64encode(data_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{base64_str}"