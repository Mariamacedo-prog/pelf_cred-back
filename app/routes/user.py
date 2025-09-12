from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.user_utils import criar_user
from app.models.User import User
from app.models.Endereco import Endereco
from app.connection.database import get_db
from app.schemas.Auth import LoginResponse
from app.schemas.Endereco import EnderecoRequest
from app.schemas.User import UserRequest, UserResponse

router = APIRouter()

@router.post("/api/v1/novo/user",response_model=LoginResponse, tags=["User"])
async def novo_usuario(form_data: UserRequest,
    db: AsyncSession = Depends(get_db)):
    queryCpf = select(User).where(User.cpf == form_data.cpf)
    resultCpf = await db.execute(queryCpf)
    userCpf = resultCpf.scalar_one_or_none()
    if userCpf:
        raise HTTPException(status_code=400, detail=f"Este CPF ({form_data.cpf}) já está vinculado a um cadastro existente.")


    queryEmail = select(User).where(User.email == form_data.email)
    resultEmail = await db.execute(queryEmail)
    userEmail = resultEmail.scalar_one_or_none()
    if userEmail:
        raise HTTPException(status_code=400, detail=f"Este E-mail ({form_data.email}) já está vinculado a um cadastro existente.")


    if form_data.username:
        queryUserName = select(User).where(User.username == form_data.username)
        resultUserName = await db.execute(queryUserName)
        userUserName = resultUserName.scalar_one_or_none()
        if userUserName:
            raise HTTPException(status_code=400,
                                detail=f"Este Username ({form_data.username}) já está vinculado a um cadastro existente.")

    res = await criar_user(form_data, db)

    return res


@router.get("/api/v1/user/{id}",response_model=UserResponse,  tags=["User"])
async def novo_usuario(id: UUID,
    db: AsyncSession = Depends(get_db)):

    query = select(User).where(User.id == id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=400, detail="Usuário não localizado na base de dados.")

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


@router.delete("/api/v1/user/{id}", tags=["User"])
async def deletar_usuario(id: UUID, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.id == id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado."
        )

    user.disabled = True
    user.deleted_at = datetime.utcnow()

    await db.commit()
    return {"detail": f"Usuário desativado com sucesso."}