from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth_utils import verificar_token, passou_do_horario
from app.core.transacao_utils import listar, por_id, atualizar, total
from app.connection.database import get_db
from app.schemas.TransacaoSchema import PaginatedTransacaoResponse, TransacaoResponse, TransacaoUpdate, TransacaoTotais

router = APIRouter()


@router.get("/api/v1/transacoes", response_model=PaginatedTransacaoResponse, tags=["Transação"])
async def listar_transacoes(
    pagina: int = Query(1, ge=1),
    items: int = Query(10, ge=1, le=15000),
    contrato_id: Optional[UUID] = Query(None),
    filtro: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token)
):
    res = await listar(pagina, items, contrato_id, filtro, db)

    return res


@router.get("/api/v1/transacoes/dashboard/resumo", response_model=TransacaoTotais, tags=["Transação"])
async def transacao_dashboard(
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token)
):
    res = await total(data_inicio, data_fim, db, user_id)
    return res



@router.get("/api/v1/transacao/{id}", response_model=TransacaoResponse,  tags=["Transação"])
async def transacao_por_id(id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token)):

    res = await por_id(id, db)

    return res



@router.put("/api/v1/transacao/{id}", tags=["Transação"])
async def atualizar_transacao(id: UUID, form_data: TransacaoUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token)
    ):
    if passou_do_horario():
        raise HTTPException(status_code=400, detail=f"Horário não permitido.")

    res = await atualizar(id, form_data, db, user_id)

    return res