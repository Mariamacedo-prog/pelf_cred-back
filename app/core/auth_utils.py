import uuid

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def gerar_token(user, duration_token=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    expires = datetime.now(timezone.utc) + duration_token
    info = {
        "id": str(user.id),
        "cpf": str(user.cpf),
        "username": str(user.username),
        "telefone": str(user.telefone),
        "email": str(user.email),
        "exp": int(expires.timestamp())
    }
    jwt_encoded = jwt.encode(info, SECRET_KEY, algorithm=ALGORITHM)
    return jwt_encoded


async def verificar_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: usuário não encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

