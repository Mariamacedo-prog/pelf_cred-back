import uuid
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse

from app.core.auth_utils import verificar_token
from app.core.log_utils import limpar_dict_para_json
from app.core.user_utils import criar_user, user_por_id, listar_users, atualizar_user
from app.models.Log import Log
from app.models.User import User
from app.connection.database import get_db
from app.schemas.Auth import LoginResponse
from app.schemas.User import UserRequest, UserResponse, PaginatedUserResponse, UserUpdate

router = APIRouter()


@router.get("/api/v1/users", response_model=PaginatedUserResponse, tags=["User"])
async def listar_usuarios(
    pagina: int = Query(1, ge=1),
    items: int = Query(10, ge=1, le=100),
    filtro: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token)
):
    res = await listar_users(pagina, items,filtro, db)

    return res


@router.get("/api/v1/user/{id}",response_model=UserResponse,  tags=["User"])
async def usuario_por_id(id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token)):

    query = select(User).where(User.id == id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=400, detail="Usuário não localizado na base de dados.")

    res = await user_por_id(id, user, db )

    return res


@router.post("/api/v1/novo/user",response_model=LoginResponse, tags=["User"])
async def novo_usuario(form_data: UserRequest,
    db: AsyncSession = Depends(get_db)):
    queryCpf = select(User).where(User.cpf == form_data.cpf)
    resultCpf = await db.execute(queryCpf)
    userCpf = resultCpf.scalar_one_or_none()
    if userCpf:
        raise HTTPException(status_code=400, detail=f"Este CPF já está vinculado a um cadastro existente.")


    queryEmail = select(User).where(User.email == form_data.email)
    resultEmail = await db.execute(queryEmail)
    userEmail = resultEmail.scalar_one_or_none()
    if userEmail:
        raise HTTPException(status_code=400, detail=f"Este E-mail já está vinculado a um cadastro existente.")


    if form_data.username:
        queryUserName = select(User).where(User.username == form_data.username)
        resultUserName = await db.execute(queryUserName)
        userUserName = resultUserName.scalar_one_or_none()
        if userUserName:
            raise HTTPException(status_code=400,
                                detail=f"Este Username já está vinculado a um cadastro existente.")

    res = await criar_user(form_data, db)

    return res



@router.put("/api/v1/user/{id}", tags=["User"])
async def atualizar_usuario(id: UUID, form_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token)
    ):

    if form_data.cpf:
        queryCpf = select(User).where(
            and_(
                User.cpf == form_data.cpf,
                User.disabled == False,
                User.id != id,
            )
        )
        resultCpf = await db.execute(queryCpf)
        userCpf = resultCpf.scalar_one_or_none()
        if userCpf:
            raise HTTPException(status_code=400, detail=f"Este CPF já está vinculado a um outro cadastro.")

    if form_data.email:
        queryEmail = select(User).where(
            and_(
                User.email == form_data.email,
                User.disabled == False,
                User.id != id,
            )
        )
        resultEmail = await db.execute(queryEmail)
        userEmail = resultEmail.scalar_one_or_none()
        if userEmail:
            raise HTTPException(status_code=400, detail=f"Este E-mail já está vinculado a um outro cadastro.")


    if form_data.username:
        queryUserName = select(User).where(
            and_(
                User.username == form_data.username,
                User.disabled == False,
                User.id != id,
            )
        )
        resultUserName = await db.execute(queryUserName)
        userUserName = resultUserName.scalar_one_or_none()
        if userUserName:
            raise HTTPException(status_code=400,
                                detail=f"Este Username já está vinculado a um cadastro existente.")

    res = await atualizar_user(id, form_data, db, user_id)

    return res



@router.delete("/api/v1/user/{id}", tags=["User"])
async def deletar_usuario(id: UUID, db: AsyncSession = Depends(get_db), user_id: str = Depends(verificar_token)):
    query = select(User).where(User.id == id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado."
        )


    dados_antigos = limpar_dict_para_json(user)

    user.disabled = True
    user.deleted_at = datetime.utcnow()

    dados_novos = limpar_dict_para_json(user)

    log = Log(
        tabela_afetada="usuario",
        operacao="DELETE",
        registro_id=user.id,
        dados_antes=dados_antigos,
        dados_depois=dados_novos,
        usuario_id=uuid.UUID(user_id)
    )

    db.add(log)
    await db.commit()

    return JSONResponse(
        content={"detail": "Usuario deletado com sucesso"},
        media_type="application/json; charset=utf-8"
    )

