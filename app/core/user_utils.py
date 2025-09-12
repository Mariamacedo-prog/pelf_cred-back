import uuid

import bcrypt
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from app.connection.database import get_db
from app.core.auth_utils import gerar_token
from app.models.Endereco import Endereco
from app.models.User import User
from app.schemas.Auth import LoginResponse
from app.schemas.User import UserInDB, UserRequest


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


async def criar_user(form_data: UserRequest,
    db: AsyncSession = Depends(get_db)):

    endereco_id = None
    if form_data.endereco:
        endereco_data = form_data.endereco
        novo_endereco = Endereco(
            id=uuid.uuid4(),
            cep=endereco_data.cep,
            rua=endereco_data.rua,
            numero=endereco_data.numero,
            bairro=endereco_data.bairro,
            complemento=endereco_data.complemento,
            cidade=endereco_data.cidade,
            uf=endereco_data.uf
        )
        db.add(novo_endereco)
        await db.flush()
        endereco_id = novo_endereco.id

    form_data.id = uuid.uuid4()

    access_token = gerar_token(form_data, timedelta(days=7))
    hash_senha = bcrypt.hashpw(form_data.senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    novo_user = User(
        id=form_data.id,
        nome=form_data.nome,
        username=form_data.username,
        cpf=form_data.cpf,
        email=form_data.email,
        telefone=form_data.telefone,
        disabled=False,
        hashed_senha=hash_senha,
        endereco_id=endereco_id,
        token=access_token
    )

    db.add(novo_user)
    await db.commit()
    await db.refresh(novo_user)

    jwt_token = LoginResponse(
        access_token=access_token,
        refresh_token=access_token,
        token_type="Bearer",
    )
    return jwt_token
