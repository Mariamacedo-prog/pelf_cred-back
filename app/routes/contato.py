
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth_utils import verificar_token, passou_do_horario
from app.core.contato_utils import por_contrato_id, por_id, criar
from app.connection.database import get_db
from app.schemas.ContatoSchema import ContatoResponse, ContatoRequest, PaginatedContatosResponse

router = APIRouter()

@router.get("/api/v1/contato/{id}", response_model=ContatoResponse,  tags=["Contato"])
async def contato_por_id(id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token)):

    res = await por_id(id, db)

    return res

@router.get("/api/v1/contatos/{contrato_id}", response_model=PaginatedContatosResponse,  tags=["Contato"])
async def contato_por_contrato_id(contrato_id: UUID,
    pagina: int = Query(1, ge=1),
    items: int = Query(10, ge=1, le=15000),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token)):

    res = await por_contrato_id(contrato_id, pagina, items, db)

    return res


@router.post("/api/v1/contato", tags=["Contato"])
async def criar_contato( form_data: ContatoRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token)
    ):
    if passou_do_horario():
        raise HTTPException(status_code=400, detail=f"Horário não permitido.")

    res = await criar(form_data, db, user_id)

    return res