import uuid
import httpx
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
from app.core.cliente_utils import criar, listar_por_id, listar, atualizar
from app.models.Cliente import Cliente
from app.models.Log import Log

from app.connection.database import get_db
from app.schemas.Cliente import ClienteResponse, ClienteRequest, PaginatedClienteResponse, ClienteUpdate

router = APIRouter()

@router.get("/api/v1/clientes", response_model=PaginatedClienteResponse, tags=["Cliente"])
async def listar_clientes(
    pagina: int = Query(1, ge=1),
    items: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    data_cadastro: Optional[datetime] = Query(None),
    disabled: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token)
):
    res = await listar(pagina, items,search,data_cadastro,disabled, db)

    return res


@router.get("/api/v1/cliente/{id}",response_model=ClienteResponse,  tags=["Cliente"])
async def cliente_por_id(id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token)):

    query = select(Cliente).where(Cliente.id == id)
    result = await db.execute(query)
    cliente = result.scalar_one_or_none()
    if not cliente:
        raise HTTPException(status_code=400, detail="Cliente/Empresa não localizado na base de dados.")

    res = await listar_por_id(id, cliente, db )

    return res


@router.post("/api/v1/novo/cliente", tags=["Cliente"])
async def novo_cliente(form_data: ClienteRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token) ):
    queryDocumento = select(Cliente).where(Cliente.documento == form_data.documento)
    resultDocumento = await db.execute(queryDocumento)
    clienteDocumento = resultDocumento.scalar_one_or_none()
    if clienteDocumento:
        raise HTTPException(status_code=400, detail=f"Este Documento já está vinculado a um cliente existente.")

    res = await criar(form_data, db, user_id)

    return res



@router.put("/api/v1/cliente/{id}", tags=["Cliente"])
async def atualizar_cliente(id: UUID, form_data: ClienteUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token)
    ):

    if form_data.documento:
        queryDocumento = select(Cliente).where(
            and_(
                Cliente.documento == form_data.documento,
                Cliente.disabled == False,
                Cliente.id != id,
            )
        )
        resultDocumento = await db.execute(queryDocumento)
        userDocumento = resultDocumento.scalar_one_or_none()
        if userDocumento:
            raise HTTPException(status_code=400, detail=f"Este Documento já está vinculado a um outro cadastro.")

    res = await atualizar(id, form_data, db, user_id)

    return res



@router.delete("/api/v1/cliente/{id}", tags=["Cliente"])
async def deletar_cliente(id: UUID, db: AsyncSession = Depends(get_db), user_id: str = Depends(verificar_token)):
    query = select(Cliente).where(Cliente.id == id)
    result = await db.execute(query)
    cliente = result.scalar_one_or_none()

    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado."
        )


    dados_antigos = limpar_dict_para_json(cliente)

    cliente.disabled = True
    cliente.deleted_at = datetime.utcnow()
    cliente.deleted_by = uuid.UUID(user_id)

    dados_novos = limpar_dict_para_json(cliente)

    log = Log(
        tabela_afetada="clientes",
        operacao="DELETE",
        registro_id=cliente.id,
        dados_antes=dados_antigos,
        dados_depois=dados_novos,
        usuario_id=uuid.UUID(user_id)
    )

    db.add(log)
    await db.commit()

    return JSONResponse(
        content={"detail": "Cliente deletado com sucesso"},
        media_type="application/json; charset=utf-8"
    )


@router.get("/api/v1/receita/{cnpj}", tags=["Cliente"])
async def get_cnpj(cnpj: str):
    url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            if response.status_code == 404:
                raise HTTPException(status_code=response.status_code, detail="Não localizado!")
            if response.status_code != 404:
                raise HTTPException(status_code=response.status_code, detail="Erro na API Receitaws, tente novamente mais tarde!")
        return response.json()


@router.get("/api/v1/cnpja/{cnpj}", tags=["Cliente"])
async def get_cnpj_cnpja(cnpj: str):
    url = f"https://open.cnpja.com/office/{cnpj}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            if response.status_code == 404:
                raise HTTPException(status_code=response.status_code, detail="Não localizado!")
            if response.status_code != 404:
                raise HTTPException(status_code=response.status_code, detail="Erro na API Cnpja, tente novamente mais tarde!")
        return response.json()