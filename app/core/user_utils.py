import uuid
from typing import Optional

import bcrypt
from fastapi import Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from starlette import status
from starlette.responses import JSONResponse

from app.connection.database import get_db
from app.core.auth_utils import gerar_token, verificar_token
from app.core.log_utils import limpar_dict_para_json
from app.models.EnderecoModel import EnderecoModel
from app.models.LogModel import LogModel
from app.models.UserModel import UserModel
from sqlalchemy import or_, func
from sqlalchemy.orm import joinedload
from app.schemas.AuthSchema import LoginResponse
from app.schemas.EnderecoSchema import EnderecoRequest
from app.schemas.UserSchema import UserInDB, UserRequest, UserResponse, UserUpdate
from sqlalchemy.future import select


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


async def criar_user(form_data: UserRequest,
    db: AsyncSession = Depends(get_db)):

    endereco_id = None
    if form_data.endereco:
        endereco_data = form_data.endereco
        novo_endereco = EnderecoModel(
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

    novo_user = UserModel(
        id=form_data.id,
        nome=form_data.nome,
        username=form_data.username,
        cpf=form_data.cpf,
        email=form_data.email,
        telefone=form_data.telefone,
        ativo=True,
        hashed_senha=hash_senha,
        endereco_id=endereco_id,
        token=access_token
    )

    db.add(novo_user)

    dados_antigos = None
    dados_novos = limpar_dict_para_json(form_data)

    log = LogModel(
        tabela_afetada="usuarios",
        operacao="CREATE",
        registro_id=form_data.id,
        dados_antes=dados_antigos,
        dados_depois=dados_novos,
        usuario_id=form_data.id
    )

    db.add(log)
    
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
    queryEndereco = select(EnderecoModel).where(EnderecoModel.id == user.endereco_id)
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


async def listar_users(
    pagina: int = Query(1, ge=1),
    items: int = Query(10, ge=1, le=100),
    filtro: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    offset = (pagina - 1) * items

    # Construir filtro
    where_clause = [UserModel.ativo == True]
    if filtro:
        filtro_str = f"%{filtro.lower()}%"
        where_clause.append(
            or_(
                func.lower(UserModel.nome).ilike(filtro_str),
                func.lower(UserModel.cpf).ilike(filtro_str)
            )
        )

    total_query = select(func.count(UserModel.id)).where(*where_clause)
    total_result = await db.execute(total_query)
    total_items = total_result.scalar()

    total_paginas = (total_items + items - 1) // items if total_items > 0 else 0

    query = (
        select(UserModel)
        .options(joinedload(UserModel.endereco))
        .where(*where_clause)
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
                   db: AsyncSession = Depends(get_db), user_id: str = Depends(verificar_token)):
    result = await db.execute(select(UserModel).where(UserModel.id == id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    dados_antigos = limpar_dict_para_json(user)

    user.updated_by = uuid.UUID(user_id)

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
    if form_data.senha is not None:
        hash_senha = bcrypt.hashpw(form_data.senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        user.hash_senha = hash_senha

    if form_data.endereco:
        if user.endereco_id:
            result = await db.execute(select(EnderecoModel).where(EnderecoModel.id == user.endereco_id))
            endereco = result.scalar_one_or_none()
        else:
            endereco = EnderecoModel(id=uuid.uuid4())
            db.add(endereco)
            user.endereco_id = endereco.id

        endereco_data = form_data.endereco
        dados_antigos_endereco = limpar_dict_para_json(endereco)

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

        dados_novos_endereco = limpar_dict_para_json(endereco)
        log_endereco = LogModel(
            tabela_afetada="endereco",
            operacao="UPDATE",
            registro_id=user.id,
            dados_antes=dados_antigos_endereco,
            dados_depois=dados_novos_endereco,
            usuario_id=uuid.UUID(user_id)
        )

        db.add(log_endereco)

    dados_novos = limpar_dict_para_json(user)
    log = LogModel(
        tabela_afetada="usuarios",
        operacao="UPDATE",
        registro_id=user.id,
        dados_antes=dados_antigos,
        dados_depois=dados_novos,
        usuario_id=uuid.UUID(user_id)
    )

    db.add(log)

    await db.commit()
    await db.refresh(user)

    return JSONResponse(
        content={"detail": "Usuário atualizado com sucesso"},
        media_type="application/json; charset=utf-8"
    )

