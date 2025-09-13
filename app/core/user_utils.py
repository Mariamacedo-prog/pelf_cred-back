import uuid

import bcrypt
from fastapi import Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from starlette import status

from app.connection.database import get_db
from app.core.auth_utils import gerar_token
from app.models.Endereco import Endereco
from app.models.User import User
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from app.schemas.Auth import LoginResponse
from app.schemas.Endereco import EnderecoRequest
from app.schemas.User import UserInDB, UserRequest, UserResponse, UserUpdate
from sqlalchemy.future import select


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


async def criar_user(form_data: UserRequest,
    db: AsyncSession = Depends(get_db), ):

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


async def user_por_id(id: uuid.UUID, user: UserResponse,
                   db: AsyncSession = Depends(get_db)):
    queryEndereco = select(Endereco).where(Endereco.id == user.endereco_id)
    resultEndereco = await db.execute(queryEndereco)
    userEndereco = resultEndereco.scalar_one_or_none()

    endereco = None

    if userEndereco:
        endereco = EnderecoRequest(
            id=userEndereco.id,
            cep=userEndereco.cep,
            rua=userEndereco.rua,
            numero=userEndereco.numero,
            bairro=userEndereco.bairro,
            complemento=userEndereco.complemento,
            cidade=userEndereco.cidade,
            uf=userEndereco.uf
        )

    usuario = UserResponse(
        id=id,
        username=user.username,
        nome=user.nome,
        cpf=user.cpf,
        email=user.email,
        telefone=user.telefone,
        created_at=user.created_at,
        updated_at=user.updated_at,
        deleted_at=user.deleted_at,
        endereco=endereco,
    )

    return usuario


async def listar_users(pagina: int = Query(1, ge=1),
    items: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)):

    offset = (pagina - 1) * items

    total_query = select(func.count(User.id))
    total_result = await db.execute(total_query)
    total_items = total_result.scalar()

    total_paginas = (total_items + items - 1) // items if total_items > 0 else 0

    query = (
        select(User)
        .options(joinedload(User.endereco))
        .offset(offset)
        .limit(items)
    )
    result = await db.execute(query)
    users = result.scalars().unique().all()

    user_list = []
    for user in users:
        endereco = None
        if user.endereco:
            endereco = EnderecoRequest(
                id=user.endereco.id,
                cep=user.endereco.cep,
                rua=user.endereco.rua,
                numero=user.endereco.numero,
                bairro=user.endereco.bairro,
                complemento=user.endereco.complemento,
                cidade=user.endereco.cidade,
                uf=user.endereco.uf
            )

        user_response = UserResponse(
            id=user.id,
            username=user.username,
            nome=user.nome,
            cpf=user.cpf,
            email=user.email,
            telefone=user.telefone,
            created_at=user.created_at,
            updated_at=user.updated_at,
            deleted_at=user.deleted_at,
            endereco=endereco,
        )

        user_list.append(user_response)

    return {
        "total_items": total_items,
        "total_paginas": total_paginas,
        "pagina_atual": pagina,
        "items": items,
        "offset": offset,
        "data": user_list
    }


async def atualizar_user(id: uuid.UUID, form_data: UserUpdate,
                   db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    if form_data.nome is not None:
        user.nome = form_data.nome
    if form_data.username is not None:
        user.username = form_data.username
    if form_data.cpf is not None:
        user.cpf = form_data.cpf
    if form_data.email is not None:
        user.email = form_data.email
    if form_data.telefone is not None:
        user.telefone = form_data.telefone


    if form_data.endereco:
        if user.endereco_id:
            result = await db.execute(select(Endereco).where(Endereco.id == user.endereco_id))
            endereco = result.scalar_one_or_none()
        else:
            endereco = Endereco(id=uuid.uuid4())
            db.add(endereco)
            user.endereco_id = endereco.id

        endereco_data = form_data.endereco

        if endereco_data.cep is not None:
            endereco.cep = endereco_data.cep
        if endereco_data.rua is not None:
            endereco.rua = endereco_data.rua
        if endereco_data.numero is not None:
            endereco.numero = endereco_data.numero
        if endereco_data.bairro is not None:
            endereco.bairro = endereco_data.bairro
        if endereco_data.complemento is not None:
            endereco.complemento = endereco_data.complemento
        if endereco_data.cidade is not None:
            endereco.cidade = endereco_data.cidade
        if endereco_data.uf is not None:
            endereco.uf = endereco_data.uf

        db.add(endereco)

    await db.commit()
    await db.refresh(user)

    return {"detail": "Usuário atualizado com sucesso"}

