import uuid
from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date

from sqlalchemy.orm import joinedload
from starlette.responses import JSONResponse
from decimal import Decimal
from app.Enum.StatusComprovante import StatusComprovante
from app.Enum.StatusParcela import StatusParcela
from app.connection.database import get_db
from app.core.anexo_utils import base64_to_bytes, bytes_to_base64
from app.core.auth_utils import verificar_token
from app.core.log_utils import limpar_dict_para_json
from app.models.AnexoModel import AnexoModel
from app.models.ContratoModel import ContratoModel
from app.models.EnderecoModel import EnderecoModel
from app.models.LogModel import LogModel
from sqlalchemy import func, and_, update

from sqlalchemy.future import select

from app.models.TransacaoModel import TransacaoModel
from app.schemas.AnexoSchema import AnexoRequest
from app.schemas.ClienteSchema import ClienteContratoResponse
from app.schemas.ContratoSchema import ContratoResponse
from app.schemas.EnderecoSchema import EnderecoRequest
from app.schemas.ParcelamentoSchema import ParcelamentoResponse
from app.schemas.TransacaoSchema import TransacaoUpdate, PaginatedTransacaoResponse, TransacaoResponse, TransacaoTotais, \
    TransacaoResponseAtraso, PaginatedTransacaoResponseAtraso
from app.schemas.VendedorSchema import VendedorContratoResponse


async def listar(
    pagina: int = Query(1, ge=1),
    items: int = Query(10, ge=1, le=15000),
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
            valor_pago=transacao.valor_pago,
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
    if form_data.status_parcela is not None:
        transacao.status_parcela = form_data.status_parcela
    if form_data.meio_pagamento is not None:
        transacao.meio_pagamento = form_data.meio_pagamento
    if form_data.status_comprovante is not None:
        transacao.status_comprovante = form_data.status_comprovante

    valor_pago = transacao.valor_pago
    if form_data.valor_pago is not None:
        valor_pago = valor_pago + Decimal(str(form_data.valor_pago))

    transacao.valor_pago = valor_pago
    if valor_pago >= transacao.valor:
        transacao.status_parcela = StatusParcela.PAGA.value
    else:
        transacao.status_parcela = StatusParcela.PAGAMENTO_PARCIAL.value

    anexo = form_data.anexo
    if anexo is not None:
        transacao.status_comprovante = StatusComprovante.EM_ANALISE.value
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
            TransacaoModel.status_parcela == StatusParcela.GERADO.value,
            TransacaoModel.data_vencimento < hoje
        )
        .values(status_parcela=StatusParcela.EM_ATRASO.value)
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

    queryEmPagamento = select(
        TransacaoModel.status_parcela,
        func.sum(TransacaoModel.valor_pago).label("total")
    )
    queryEmPagamento = queryEmPagamento.group_by(TransacaoModel.status_parcela)
    resEmPagamento = await db.execute(queryEmPagamento)
    resultadosEmPagamento = {row.status_parcela: row.total or 0 for row in resEmPagamento.fetchall()}


    totais = TransacaoTotais(
        total_gerado=resultados.get("GERADO", 0),
        total_pago=resultados.get("PAGA", 0) + resultadosEmPagamento.get("PAGAMENTO_PARCIAL", 0),
        total_em_atraso=resultados.get("EM_ATRASO", 0),
        total_cancelado=resultados.get("CANCELADO", 0)
    )

    return totais


async def listar_em_atraso(
    pagina: int = Query(1, ge=1),
    items: int = Query(10, ge=1, le=15000),
    filtro: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    offset = (pagina - 1) * items
    hoje = date.today()
    stmt_update = (
        update(TransacaoModel)
        .where(
            TransacaoModel.status_parcela == StatusParcela.GERADO.value,
            TransacaoModel.data_vencimento < hoje
        )
        .values(status_parcela=StatusParcela.EM_ATRASO.value)
    )
    await db.execute(stmt_update)
    await db.commit()

    # Apenas vencidos
    dias_em_atraso = func.date_part(
        'day',
        func.now() - TransacaoModel.data_vencimento
    )

    where_clause = []

    where_clause.append(TransacaoModel.status_parcela == StatusParcela.EM_ATRASO.value)
    if filtro is not None:
        if filtro == "7":
            where_clause.append(
                and_(
                    TransacaoModel.data_vencimento < func.now(),
                    dias_em_atraso <= 7
                )
            )
        elif filtro == "30":
            where_clause.append(
                and_(
                    TransacaoModel.data_vencimento < func.now(),
                    dias_em_atraso.between(8, 30)
                )
            )
        elif filtro == "30+":
            where_clause.append(
                and_(
                    TransacaoModel.data_vencimento < func.now(),
                    dias_em_atraso > 30
                )
            )

    total_query = select(func.count(TransacaoModel.id)).where(*where_clause)
    total_result = await db.execute(total_query)
    total_items = total_result.scalar()

    total_paginas = (total_items + items - 1) // items if total_items > 0 else 0

    query = select(TransacaoModel).where(*where_clause)

    query = query.offset(offset).limit(items)

    result = await db.execute(query)
    transacoes = result.scalars().unique().all()

    transacoes_list = []
    for transacao in transacoes:
        queryContrato = select(ContratoModel).options(
            joinedload(ContratoModel.parcelamento),
            joinedload(ContratoModel.responsavel_assinatura),
            joinedload(ContratoModel.cliente_assinatura),
            joinedload(ContratoModel.cliente),
            joinedload(ContratoModel.vendedor),
        ).where(ContratoModel.id == transacao.contrato_id)

        resultContrato = await db.execute(queryContrato)
        contrato = resultContrato.scalar_one_or_none()
        if not contrato:
            raise HTTPException(status_code=400, detail="Contrato não localizado na base de dados.")

        parcelamento = None
        if contrato.parcelamento:
            parcelamento = ParcelamentoResponse(
                id=contrato.parcelamento.id,
                data_inicio=contrato.parcelamento.data_inicio,
                data_fim=contrato.parcelamento.data_fim,
                data_vigencia=contrato.parcelamento.data_vigencia,
                meio_pagamento=contrato.parcelamento.meio_pagamento,
                valor_total=contrato.parcelamento.valor_total,
                valor_parcela=contrato.parcelamento.valor_parcela,
                valor_entrada=contrato.parcelamento.valor_entrada,
                qtd_parcela=contrato.parcelamento.qtd_parcela,
                avista=contrato.parcelamento.avista,
                taxa_juros=contrato.parcelamento.taxa_juros,
                data_ultimo_pagamento=contrato.parcelamento.data_ultimo_pagamento,
                qtd_parcelas_pagas=contrato.parcelamento.qtd_parcelas_pagas,
                ativo=contrato.parcelamento.ativo,
                tipo_pagamento=contrato.parcelamento.tipo_pagamento,
                created_at=contrato.parcelamento.created_at,
                updated_at=contrato.parcelamento.updated_at,
                deleted_at=contrato.parcelamento.deleted_at,
                created_by=contrato.parcelamento.created_by,
                updated_by=contrato.parcelamento.updated_by,
                deleted_by=contrato.parcelamento.deleted_by,
            )

        cliente = None
        if contrato.cliente:
            endereco_cliente = None
            query = select(EnderecoModel).where(
                and_(
                    EnderecoModel.id == contrato.cliente.endereco_id,
                )
            )

            result = await db.execute(query)
            item = result.scalar_one_or_none()
            if item:
                endereco_cliente = EnderecoRequest(
                    id=item.id,
                    cep=item.cep,
                    rua=item.rua,
                    numero=item.numero,
                    bairro=item.bairro,
                    complemento=item.complemento,
                    cidade=item.cidade,
                    uf=item.uf,
                )

            cliente = ClienteContratoResponse(
                id=contrato.cliente.id,
                nome=contrato.cliente.nome,
                documento=contrato.cliente.documento,
                email=contrato.cliente.email,
                telefone=contrato.cliente.telefone,
                grupo_segmento=contrato.cliente.grupo_segmento,
                ativo=contrato.cliente.ativo,
                endereco=endereco_cliente
            )

        vendedor = None
        if contrato.vendedor:
            vendedor = VendedorContratoResponse(
                id=contrato.vendedor.id,
                nome=contrato.vendedor.nome,
                cpf=contrato.vendedor.cpf,
                email=contrato.vendedor.email,
                telefone=contrato.vendedor.telefone,
                rg=contrato.vendedor.rg,
                ativo=contrato.vendedor.ativo
            )

        contrato_response = ContratoResponse(
            id=contrato.id,
            numero=contrato.numero,
            nome=contrato.nome,
            documento=contrato.documento,
            ativo=contrato.ativo,
            status_cobranca=contrato.status_cobranca,
            status_contrato=contrato.status_contrato,
            parcelamento=parcelamento,
            cliente=cliente,
            vendedor=vendedor,
            anexos_list=None,
            responsavel_assinatura=None,
            cliente_assinatura=None,
            created_at=contrato.created_at,
            updated_at=contrato.updated_at,
            deleted_at=contrato.deleted_at,
            created_by=contrato.created_by,
            updated_by=contrato.updated_by,
            deleted_by=contrato.deleted_by,
        )


        transacao_response = TransacaoResponseAtraso(
            id=transacao.id,
            valor=transacao.valor,
            contrato=contrato_response,
            valor_pago=transacao.valor_pago,
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

    return PaginatedTransacaoResponseAtraso(
        total_items=total_items,
        total_paginas=total_paginas,
        pagina_atual=pagina,
        items=items,
        offset=offset,
        data=transacoes_list
    )
