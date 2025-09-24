from fastapi import APIRouter
from typing import Optional
from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.connection.database import get_db
from app.core.auth_utils import verificar_token
from app.models.EnderecoModel import EnderecoModel
from sqlalchemy import distinct, func

from sqlalchemy.future import select

from app.schemas.EnderecoSchema import CidadeResponse

router = APIRouter()

@router.get("/", tags=["Utils"])
async def root():
    return {"message": "Hello World"}

@router.get("/api/v1/cidades", tags=["Utils"])
async def listar_cidades_registradas(
    filtro: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verificar_token)
):
    # SELECT cidade, uf FROM enderecos DISTINCT
    query = select(EnderecoModel.cidade, EnderecoModel.uf).distinct()

    # Filtro opcional
    if filtro:
        filtro_str = f"%{filtro.lower()}%"
        query = query.where(func.lower(EnderecoModel.cidade).ilike(filtro_str))

    result = await db.execute(query)
    cidades_unicas = result.all()

    # Monta a resposta
    cidades_list = [
        CidadeResponse(cidade=cidade, uf=uf)
        for cidade, uf in cidades_unicas
    ]

    return cidades_list