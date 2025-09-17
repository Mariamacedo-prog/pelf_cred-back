from datetime import timedelta

import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, and_
from app.core.auth_utils import gerar_token, verificar_token
from app.schemas.Auth import LoginRequest, LoginResponse
from app.models.User import User
from app.connection.database import get_db

router = APIRouter()

@router.post("/api/v1/login", response_model=LoginResponse, tags=["Auth"])
async def login(
    form_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    query = select(User).where(
        and_(
            User.cpf == form_data.login,
            User.disabled == False
        ))
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=400, detail="Usuário ou senha inválidos")

    if not bcrypt.checkpw(form_data.senha.encode('utf-8'), user.hashed_senha.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Usuário ou senha inválidos")

    new_token = gerar_token(user)
    refresh_token = gerar_token(user, timedelta(days=7))
    stmt = (
        update(User)
        .where(User.cpf == form_data.login)
        .values(token=refresh_token)
    )

    await db.execute(stmt)
    await db.commit()

    jwt_token = LoginResponse(
        access_token=new_token,
        refresh_token=refresh_token,
        token_type="Bearer",
    )

    return jwt_token


@router.get("/api/v1/refresh", response_model=LoginResponse, tags=["Auth"])
async def refresh(token: str, db: AsyncSession = Depends(get_db)):
    user = await verificar_token(token, db)

    if not user:
        raise HTTPException(status_code=400, detail="Usuário não localizado")

    access_token = gerar_token(user)
    refresh_token = gerar_token(user, timedelta(days=7))
    jwt_token = LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
    )

    return jwt_token