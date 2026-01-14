from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth_utils import verificar_token, passou_do_horario
from app.core.servico_utils import listar, criar, por_id, atualizar, delete
from app.connection.database import get_db
from app.schemas.ServicoSchema import PaginatedServicoResponse, ServicoRequest, ServicoBase, ServicoUpdate, PaginatedServicoListResponse

router = APIRouter()


@router.get("/api/v1/servicos", response_model=PaginatedServicoResponse, tags=["Serviço"])
async def listar_servicos(
    pagina: int = Query(1, ge=1),
    items: int = Query(10, ge=1, le=15000),
    filtro: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token)
):
    res = await listar(pagina, items,filtro, db)

    return res


@router.get("/api/v1/servicos/info", response_model=PaginatedServicoListResponse, tags=["Serviço"])
async def listar_servicos_simples(
    pagina: int = Query(1, ge=1),
    items: int = Query(10, ge=1, le=100000),
    filtro: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token)
):
    res = await listar(pagina, items,filtro, db)

    return res


@router.get("/api/v1/servico/{id}", response_model=ServicoBase,  tags=["Serviço"])
async def servico_por_id(id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token)):

    res = await por_id(id, db)

    return res


@router.post("/api/v1/novo/servico", tags=["Serviço"])
async def novo_servico(form_data: ServicoRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token)):

    if passou_do_horario():
        raise HTTPException(status_code=400, detail=f"Horário não permitido.")

    res = await criar(form_data, db, user_id)

    return res



@router.put("/api/v1/servico/{id}", tags=["Serviço"])
async def atualizar_servico(id: UUID, form_data: ServicoUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token)
    ):

    if passou_do_horario():
        raise HTTPException(status_code=400, detail=f"Horário não permitido.")

    res = await atualizar(id, form_data, db, user_id)

    return res



@router.delete("/api/v1/servico/{id}", tags=["Serviço"])
async def deletar_servico(id: UUID, db: AsyncSession = Depends(get_db), user_id: str = Depends(verificar_token)):

    if passou_do_horario():
        raise HTTPException(status_code=400, detail=f"Horário não permitido.")

    res = await delete(id, db, user_id)

    return res