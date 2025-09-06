from datetime import timedelta

import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from app.core.auth_utils import create_token, verify_token
from app.schemas.Auth import LoginRequest, LoginResponse
from app.models.User import User
from app.connection.database import get_db

router = APIRouter()

@router.post("/login", response_model=LoginResponse, tags=["Auth"])
async def login(
    form_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    query = select(User).where(User.doc == form_data.doc)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=400, detail="Usuário ou senha inválidos")

    if not bcrypt.checkpw(form_data.password.encode('utf-8'), user.hashed_password.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Usuário ou senha inválidos")

    new_token = create_token(user)
    refresh_token = create_token(user, timedelta(days=7))
    stmt = (
        update(User)
        .where(User.doc == form_data.doc)
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


@router.get("/refresh", response_model=LoginResponse, tags=["Auth"])
async def refresh(token: str, db: AsyncSession = Depends(get_db)):
    user = await verify_token(token, db)

    if not user:
        raise HTTPException(status_code=400, detail="Usuário não localizado")

    access_token = create_token(user)
    refresh_token = create_token(user, timedelta(days=7))
    jwt_token = LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
    )

    return jwt_token