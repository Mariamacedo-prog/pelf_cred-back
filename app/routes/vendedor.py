from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth_utils import verificar_token, passou_do_horario
from app.core.vendedor_utils import listar, criar, por_id, atualizar, delete
from app.connection.database import get_db
from app.schemas.VendedorSchema import  VendedorRequest, VendedorUpdate, PaginatedVendedorResponse, VendedorResponse

router = APIRouter()

@router.get("/api/v1/vendedores", response_model=PaginatedVendedorResponse, tags=["Vendedor"])
async def listar_vendedores(
    pagina: int = Query(1, ge=1),
    items: int = Query(10, ge=1, le=100),
    filtro: Optional[str] = Query(None),
    filtro_cidade: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token)
):
    res = await listar(pagina, items, filtro, filtro_cidade, db)

    return res

@router.get("/api/v1/vendedor/{id}", response_model=VendedorResponse,  tags=["Vendedor"])
async def vendedor_por_id(id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token)):

    res = await por_id(id, db)

    return res


@router.post("/api/v1/novo/vendedor", tags=["Vendedor"])
async def novo_vendedor(form_data: VendedorRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token)):
    if passou_do_horario():
        raise HTTPException(status_code=400, detail=f"Horário não permitido.")

    res = await criar(form_data, db, user_id)

    return res



@router.put("/api/v1/vendedor/{id}", tags=["Vendedor"])
async def atualizar_vendedor(id: UUID, form_data: VendedorUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token)
    ):

    if passou_do_horario():
        raise HTTPException(status_code=400, detail=f"Horário não permitido.")

    res = await atualizar(id, form_data, db, user_id)

    return res



@router.delete("/api/v1/vendedor/{id}", tags=["Vendedor"])
async def deletar_vendedor(id: UUID, db: AsyncSession = Depends(get_db), user_id: str = Depends(verificar_token)):
    if passou_do_horario():
        raise HTTPException(status_code=400, detail=f"Horário não permitido.")

    res = await delete(id, db, user_id)

    return res