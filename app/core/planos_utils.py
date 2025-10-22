import uuid
from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from starlette import status
from starlette.responses import JSONResponse

from app.connection.database import get_db
from app.core.auth_utils import verificar_token
from app.core.log_utils import limpar_dict_para_json
from app.models.ContratoModel import ContratoModel
from app.models.LogModel import LogModel
from app.models.PlanoModel import PlanoModel
from sqlalchemy import func, and_

from app.models.ServicoModel import ServicoModel
from app.schemas.PlanoSchema import PlanoBase, PlanoRequest, PlanoUpdate, PlanoServicoResponse
from sqlalchemy.future import select

from app.schemas.ServicoSchema import ServicoList


async def listar(
    pagina: int = Query(1, ge=1),
    items: int = Query(10, ge=1, le=100),
    filtro: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    offset = (pagina - 1) * items

    where_clause = [PlanoModel.ativo == True]
    if filtro:
        filtro_str = f"%{filtro.lower()}%"
        where_clause.append(func.lower(PlanoModel.nome).ilike(filtro_str))

    total_query = select(func.count(PlanoModel.id)).where(*where_clause)
    total_result = await db.execute(total_query)
    total_items = total_result.scalar()

    total_paginas = (total_items + items - 1) // items if total_items > 0 else 0

    query = (
        select(PlanoModel)
        .where(*where_clause)
        .offset(offset)
        .limit(items)
    )
    result = await db.execute(query)
    planos = result.scalars().unique().all()

    plano_list = []
    for plano in planos:
        servicos_list = []
        if plano.servicos_vinculados:
            for servico in plano.servicos_vinculados:
                query = select(ServicoModel).where(
                    and_(
                        ServicoModel.id == servico
                    )
                )
                result = await db.execute(query)
                item = result.scalar_one_or_none()

                if item:
                    servicoItem = ServicoList(
                        id=item.id,
                        nome=item.nome,
                        valor=item.valor
                    )
                    servicos_list.append(servicoItem)

        plano_response = PlanoServicoResponse(
            id=plano.id,
            nome=plano.nome,
            descricao=plano.descricao,
            valor_mensal=plano.valor_mensal,
            valor_total=plano.valor_total,
            numero_parcelas=plano.numero_parcelas,
            ativo=plano.ativo,
            avista=plano.avista,
            periodo_vigencia=plano.periodo_vigencia,
            servicos_vinculados=servicos_list
        )
        plano_list.append(plano_response)

    return {
        "total_items": total_items,
        "total_paginas": total_paginas,
        "pagina_atual": pagina,
        "items": items,
        "offset": offset,
        "data": plano_list
    }

async def por_id(id: uuid.UUID,
                   db: AsyncSession = Depends(get_db)):

    query = select(PlanoModel).where(PlanoModel.id == id)
    result = await db.execute(query)
    plano = result.scalar_one_or_none()
    if not plano:
        raise HTTPException(status_code=400, detail="Plano não localizado na base de dados.")

    return plano



async def criar(form_data: PlanoRequest,
                     db: AsyncSession = Depends(get_db), user_id: str = Depends(verificar_token)):

    queryNome = select(PlanoModel).where(PlanoModel.nome == form_data.nome)
    resultNome = await db.execute(queryNome)
    planoNome = resultNome.scalar_one_or_none()
    if planoNome:
        raise HTTPException(status_code=400, detail=f"Este Nome já está vinculado a um plano existente.")

    form_data.id = uuid.uuid4()

    if not form_data.valor_mensal:
        raise HTTPException(status_code=400, detail=f"Insira o valor mensal!")

    if form_data.valor_mensal <= 0:
        raise HTTPException(status_code=400, detail=f"Insira o valor mensal!")

    if not form_data.periodo_vigencia:
        raise HTTPException(status_code=400, detail=f"Insira o periodo vigencia!")

    total_parcelamento = 0
    if form_data.numero_parcelas:
        total_parcelamento = form_data.valor_mensal * form_data.numero_parcelas

    servicos_vinculados = None

    if form_data.servicos_vinculados is not None:
        servicos_vinculados = [
            s if isinstance(s, UUID) else UUID(s)
            for s in form_data.servicos_vinculados
        ]

    novo_plano = PlanoModel(
        id=form_data.id,
        nome=form_data.nome,
        descricao=form_data.descricao,
        valor_mensal=form_data.valor_mensal,
        valor_total=total_parcelamento,
        numero_parcelas=form_data.numero_parcelas,
        ativo=True,
        avista=form_data.avista,
        periodo_vigencia=form_data.periodo_vigencia,
        servicos_vinculados=servicos_vinculados,
        created_by=uuid.UUID(user_id)
    )

    db.add(novo_plano)

    dados_antigos = None
    dados_novos =  limpar_dict_para_json(form_data)

    log = LogModel(
        tabela_afetada="planos",
        operacao="CREATE",
        registro_id=form_data.id,
        dados_antes=dados_antigos,
        dados_depois=dados_novos,
        usuario_id=uuid.UUID(user_id)
    )

    db.add(log)

    await db.commit()
    await db.refresh(novo_plano)

    return JSONResponse(
        content={"detail": "Plano criado com sucesso"},
        media_type="application/json; charset=utf-8"
    )



async def atualizar(id: uuid.UUID, form_data: PlanoUpdate,
                   db: AsyncSession = Depends(get_db), user_id: str = Depends(verificar_token)):

    query = select(PlanoModel).where(PlanoModel.id == id)
    result = await db.execute(query)
    plano = result.scalar_one_or_none()
    if not plano:
        raise HTTPException(status_code=400, detail="Plano não localizado na base de dados.")

    if form_data.nome:
        queryNome = select(PlanoModel).where(
            and_(
                PlanoModel.nome == form_data.nome,
                PlanoModel.ativo == True,
                PlanoModel.id != id,
            )
        )
        resultNome = await db.execute(queryNome)
        planoNome = resultNome.scalar_one_or_none()
        if planoNome:
            raise HTTPException(status_code=400,
                                detail=f"Este Nome já está vinculado a um Plano existente.")

    if form_data.nome is None:
        raise HTTPException(status_code=400, detail=f"Insira o valor nome!")

    if form_data.valor_mensal is not None:
        if form_data.valor_mensal <= 0:
            raise HTTPException(status_code=400, detail=f"Insira o valor mensal!")

    if not form_data.periodo_vigencia:
        raise HTTPException(status_code=400, detail=f"Insira o periodo vigencia!")

    result = await db.execute(select(PlanoModel).where(PlanoModel.id == id))
    plano = result.scalar_one_or_none()
    if not plano:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plano não encontrado"
        )

    dados_antigos = limpar_dict_para_json(plano)

    plano.updated_by = uuid.UUID(user_id)

    if form_data.nome is not None:
        plano.nome = form_data.nome
    if form_data.descricao is not None:
        plano.descricao = form_data.descricao
    if form_data.valor_mensal is not None:
        plano.valor_mensal = form_data.valor_mensal
        if form_data.numero_parcelas is not None:
            plano.valor_total = form_data.valor_mensal * form_data.numero_parcelas
        if form_data.numero_parcelas is None:
            plano.valor_total = form_data.valor_mensal * plano.numero_parcelas
    if form_data.numero_parcelas is not None:
        plano.numero_parcelas = form_data.numero_parcelas
    if form_data.ativo is not None:
        plano.ativo = form_data.ativo
    if form_data.avista is not None:
        plano.avista = form_data.avista
    if form_data.periodo_vigencia is not None:
        plano.periodo_vigencia = form_data.periodo_vigencia

    if form_data.servicos_vinculados is not None:
        plano.servicos_vinculados = [
            s if isinstance(s, UUID) else UUID(s)
            for s in form_data.servicos_vinculados
        ]
    else:
        plano.servicos_vinculados = None

    dados_novos =  limpar_dict_para_json(plano)
    log = LogModel(
        tabela_afetada="planos",
        operacao="UPDATE",
        registro_id=plano.id,
        dados_antes=dados_antigos,
        dados_depois=dados_novos,
        usuario_id=uuid.UUID(user_id)
    )

    db.add(log)

    await db.commit()
    await db.refresh(plano)

    return JSONResponse(
        content={"detail": "Plano atualizado com sucesso"},
        media_type="application/json; charset=utf-8"
    )


async def delete(id: UUID, db: AsyncSession = Depends(get_db), user_id: str = Depends(verificar_token)):

    query = select(PlanoModel).where(PlanoModel.id == id)
    result = await db.execute(query)
    plano = result.scalar_one_or_none()

    if not plano:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plano não encontrado."
        )

    dados_antigos = limpar_dict_para_json(plano)

    message = ""

    queryContrato = select(ContratoModel).where(
        and_(
            ContratoModel.plano_id == id,
            ContratoModel.ativo == True
        ))
    resultContrato = await db.execute(queryContrato)
    contrato = resultContrato.scalar_one_or_none()

    plano.ativo = False

    if contrato:
        message = "Existe um contrato ativo para este plano. O plano será somente desabilitado."

    if not contrato:
        message = "Plano deletado com sucesso"
        plano.deleted_at = datetime.utcnow()
        plano.deleted_by = uuid.UUID(user_id)

    dados_novos = limpar_dict_para_json(plano)

    log = LogModel(
        tabela_afetada="planos",
        operacao="DELETE",
        registro_id=plano.id,
        dados_antes=dados_antigos,
        dados_depois=dados_novos,
        usuario_id=uuid.UUID(user_id)
    )

    db.add(log)
    await db.commit()

    return JSONResponse(
        content={"detail": message},
        media_type= "application/json; charset=utf-8"
    )




