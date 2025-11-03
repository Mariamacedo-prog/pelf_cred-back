import uuid
from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date
from starlette import status
from starlette.responses import JSONResponse

from app.connection.database import get_db
from app.core.anexo_utils import base64_to_bytes
from app.core.auth_utils import verificar_token
from app.core.log_utils import limpar_dict_para_json
from app.models.AnexoModel import AnexoModel
from app.models.ContratoModel import ContratoModel
from app.models.LogModel import LogModel
from app.models.PlanoModel import PlanoModel
from sqlalchemy import func, and_, update

from sqlalchemy.future import select

from app.models.TransacaoModel import TransacaoModel
from app.schemas.TransacaoSchema import TransacaoUpdate, PaginatedTransacaoResponse, TransacaoResponse, TransacaoTotais


async def listar(
    pagina: int = Query(1, ge=1),
    items: int = Query(10, ge=1, le=100),
    contrato_id: Optional[UUID] = Query(None),
    filtro: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    offset = (pagina - 1) * items

    where_clause = []
    if filtro is not None:
        filtro_str = f"%{filtro.lower()}%"
        where_clause.append(func.lower(TransacaoModel.status_parcela).ilike(filtro_str))

    if contrato_id is not None:
        where_clause.append(TransacaoModel.contrato_id == contrato_id)
        items = 100

    total_query = select(func.count(TransacaoModel.id)).where(*where_clause)
    total_result = await db.execute(total_query)
    total_items = total_result.scalar()

    total_paginas = (total_items + items - 1) // items if total_items > 0 else 0

    query = select(TransacaoModel).where(*where_clause)
    if contrato_id is not None:
        query = query.order_by(TransacaoModel.data_vencimento.asc())

    query = query.offset(offset).limit(items)

    result = await db.execute(query)
    transacoes = result.scalars().unique().all()

    transacoes_list = []
    for transacao in transacoes:
        transacao_response = TransacaoResponse(
            id=transacao.id,
            valor=transacao.valor,
            contrato_id=transacao.contrato_id,
            plano_id=transacao.plano_id,
            comprovante_numero=transacao.comprovante_numero,
            status_parcela=transacao.status_parcela,
            meio_pagamento=transacao.meio_pagamento,
            status_comprovante=transacao.status_comprovante,
            data_vencimento=transacao.data_vencimento,
            data_pagamento=transacao.data_pagamento,
            anexo_id=transacao.anexo_id,
            numero_parcela=transacao.numero_parcela,
            created_at=transacao.created_at,
            updated_at=transacao.updated_at,
            deleted_at=transacao.deleted_at,
            created_by=transacao.created_by,
            updated_by=transacao.updated_by,
            deleted_by=transacao.deleted_by,
        )
        transacoes_list.append(transacao_response)

    return PaginatedTransacaoResponse(
        total_items=total_items,
        total_paginas=total_paginas,
        pagina_atual=pagina,
        items=items,
        offset=offset,
        data=transacoes_list
    )



async def por_id(id: uuid.UUID,
                   db: AsyncSession = Depends(get_db)):

    query = select(TransacaoModel).where(TransacaoModel.id == id)
    result = await db.execute(query)
    transacao = result.scalar_one_or_none()
    if not transacao:
        raise HTTPException(status_code=400, detail="Transação não localizada na base de dados.")

    return transacao



async def atualizar(id: uuid.UUID, form_data: TransacaoUpdate,
                   db: AsyncSession = Depends(get_db), user_id: str = Depends(verificar_token)):

    result = await db.execute(select(TransacaoModel).where(TransacaoModel.id == id))
    transacao = result.scalar_one_or_none()
    if not transacao:
        raise HTTPException(status_code=400, detail="Transação não localizada na base de dados.")

    dados_antigos = limpar_dict_para_json(transacao)

    transacao.updated_by = uuid.UUID(user_id)

    if form_data.comprovante_numero is not None:
        transacao.comprovante_numero = form_data.comprovante_numero
    if form_data.data_pagamento is not None:
        transacao.data_pagamento = form_data.data_pagamento
    if form_data.data_pagamento is not None:
        transacao.data_pagamento = form_data.data_pagamento
    if form_data.status_parcela is not None:
        transacao.status_parcela = form_data.status_parcela
    if form_data.meio_pagamento is not None:
        transacao.meio_pagamento = form_data.meio_pagamento
    if form_data.status_comprovante is not None:
        transacao.status_comprovante = form_data.status_comprovante

    anexo = form_data.anexo
    if anexo is not None:
        if anexo.id:
            query_anexo_existente = select(AnexoModel).where(AnexoModel.id == anexo.id)
            result_anexo = await db.execute(query_anexo_existente)
            anexo_existente = result_anexo.scalar_one_or_none()

            if anexo_existente:
                anexo_existente.base64 = base64_to_bytes(anexo.base64)
                anexo_existente.image = anexo.image
                anexo_existente.descricao = anexo.descricao
                anexo_existente.nome = anexo.nome
                anexo_existente.tipo = anexo.tipo
                anexo_existente.updated_by = uuid.UUID(user_id)
                anexo_existente.updated_at = datetime.utcnow()

                await db.merge(anexo_existente)
        else:
            novo_item_id = uuid.uuid4()
            image_bytes = base64_to_bytes(anexo.base64)
            novo_anexo = AnexoModel(
                id=novo_item_id,
                base64=image_bytes,
                image=anexo.image,
                descricao=anexo.descricao,
                nome=anexo.nome,
                tipo=anexo.tipo,
                created_by=uuid.UUID(user_id)
            )
            db.add(novo_anexo)
            await db.flush()


    dados_novos =  limpar_dict_para_json(transacao)
    log = LogModel(
        tabela_afetada="transacoes",
        operacao="UPDATE",
        registro_id=transacao.id,
        dados_antes=dados_antigos,
        dados_depois=dados_novos,
        usuario_id=uuid.UUID(user_id)
    )

    db.add(log)

    await db.commit()
    await db.refresh(transacao)

    return JSONResponse(
        content={"detail": "Transação atualizada com sucesso"},
        media_type="application/json; charset=utf-8"
    )




async def total(
    data_inicio = None,
    data_fim = None,
    db: AsyncSession = Depends(get_db), user_id: str = Depends(verificar_token)
):
    hoje = date.today()

    stmt_update = (
        update(TransacaoModel)
        .where(
            TransacaoModel.status_parcela == "GERADO",
            TransacaoModel.data_vencimento < hoje
        )
        .values(status_parcela="EM_ATRASO")
    )
    await db.execute(stmt_update)
    await db.commit()

    query = select(
        TransacaoModel.status_parcela,
        func.sum(TransacaoModel.valor).label("total")
    )

    if data_inicio:
        query = query.where(TransacaoModel.data_vencimento >= data_inicio)
    if data_fim:
        query = query.where(TransacaoModel.data_vencimento <= data_fim)

    query = query.group_by(TransacaoModel.status_parcela)

    res = await db.execute(query)
    resultados = {row.status_parcela: row.total or 0 for row in res.fetchall()}

    totais = TransacaoTotais(
        total_gerado=resultados.get("GERADO", 0),
        total_pago=resultados.get("PAGO", 0),
        total_em_atraso=resultados.get("EM_ATRASO", 0),
        total_cancelado=resultados.get("CANCELADO", 0)
    )

    return totais