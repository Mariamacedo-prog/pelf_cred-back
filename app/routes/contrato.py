from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.Enum.StatusContrato import StatusContrato
from app.core.auth_utils import verificar_token
from app.core.contrato_utils import listar, criar, por_id, atualizar, delete_item, gerar_contrato_word, gerar_contrato_pdf, mudar_status_contrato, assinar_contrato
from app.connection.database import get_db
from app.schemas.AnexoSchema import AnexoRequest
from app.schemas.ContratoSchema import PaginateContratoResponse, ContratoResponse, ContratoRequest, ContratoUpdate

router = APIRouter()


@router.get("/api/v1/contratos", response_model=PaginateContratoResponse, tags=["Contrato"])
async def listar_contratos(
    pagina: int = Query(1, ge=1),
    items: int = Query(10, ge=1, le=100),
    filtro: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token)
):
    res = await listar(pagina, items,filtro, db)

    return res

@router.get("/api/v1/contrato/{id}", response_model=ContratoResponse,  tags=["Contrato"])
async def contrato_por_id(id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token)):

    res = await por_id(id, db)

    return res


@router.get("/api/v1/pdf/contrato/{id}", response_model=ContratoResponse,  tags=["Contrato"])
async def contrato_pdf(id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token)):

    res = await gerar_contrato_pdf(id, db)

    return res

@router.get("/api/v1/word/contrato/{id}", response_model=ContratoResponse,  tags=["Contrato"])
async def contrato_word(id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token)):

    res = await gerar_contrato_word(id, db)

    return res


@router.post("/api/v1/novo/contrato", tags=["Contrato"])
async def novo_contrato(form_data: ContratoRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token)):

    res = await criar(form_data, db, user_id)

    return res



@router.put("/api/v1/contrato/{id}", tags=["Contrato"])
async def atualizar_contrato(id: UUID, form_data: ContratoUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token)
    ):

    res = await atualizar(id, form_data, db, user_id)

    return res



@router.delete("/api/v1/contrato/{id}", tags=["Contrato"])
async def deletar_contrato(id: UUID, db: AsyncSession = Depends(get_db), user_id: str = Depends(verificar_token)):

    res = await delete_item(id, db, user_id)

    return res


@router.put("/api/v1/contrato/{id}/enviar-para-assinatura", tags=["Contrato"])
async def enviar_assinatura(id: UUID, db: AsyncSession = Depends(get_db), user_id: str = Depends(verificar_token)):
    res = await mudar_status_contrato(id, StatusContrato.PENDENTE_ASSINATURA.value, db, user_id)

    return res


@router.put("/api/v1/contrato/{id}/enviar-para-edicao", tags=["Contrato"])
async def enviar_assinatura(id: UUID, db: AsyncSession = Depends(get_db), user_id: str = Depends(verificar_token)):
    res = await mudar_status_contrato(id, StatusContrato.INICIADO.value, db, user_id)

    return res

@router.post("/api/v1/contrato/{id}/assinar/cliente", tags=["Contrato"])
async def assinatura_cliente(id: UUID, form_data: AnexoRequest, db: AsyncSession = Depends(get_db), user_id: str = Depends(verificar_token)):
    res = await assinar_contrato(id, 'cliente', form_data, db, user_id)

    return res


@router.post("/api/v1/contrato/{id}/assinar/responsavel", tags=["Contrato"])
async def assinatura_responsavel(id: UUID, form_data: AnexoRequest, db: AsyncSession = Depends(get_db), user_id: str = Depends(verificar_token)):
    res = await assinar_contrato(id, 'responsavel', form_data, db, user_id)

    return res