from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth_utils import verificar_token, passou_do_horario
from app.core.planos_utils import listar, por_id, criar, atualizar, delete
from app.connection.database import get_db
from app.schemas.PlanoSchema import PaginatedPlanoResponse, PlanoBase, PlanoRequest, PlanoUpdate

router = APIRouter()


@router.get("/api/v1/planos", response_model=PaginatedPlanoResponse, tags=["Plano"])
async def listar_planos(
    pagina: int = Query(1, ge=1),
    items: int = Query(10, ge=1, le=15000),
    filtro: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token)
):
    res = await listar(pagina, items,filtro, db)

    return res


@router.get("/api/v1/plano/{id}", response_model=PlanoBase,  tags=["Plano"])
async def plano_por_id(id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token)):

    res = await por_id(id, db)

    return res


@router.post("/api/v1/novo/plano", tags=["Plano"])
async def novo_plano(form_data: PlanoRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token)):

    if passou_do_horario():
        raise HTTPException(status_code=400, detail=f"Horário não permitido.")

    res = await criar(form_data, db, user_id)

    return res



@router.put("/api/v1/plano/{id}", tags=["Plano"])
async def atualizar_plano(id: UUID, form_data: PlanoUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token)
    ):

    if passou_do_horario():
        raise HTTPException(status_code=400, detail=f"Horário não permitido.")

    res = await atualizar(id, form_data, db, user_id)

    return res



@router.delete("/api/v1/plano/{id}", tags=["Plano"])
async def deletar_plano(id: UUID, db: AsyncSession = Depends(get_db), user_id: str = Depends(verificar_token)):

    if passou_do_horario():
        raise HTTPException(status_code=400, detail=f"Horário não permitido.")

    res = await delete(id, db, user_id)

    return res