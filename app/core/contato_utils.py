import uuid
from fastapi import Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.connection.database import get_db
from app.core.auth_utils import verificar_token
from app.core.log_utils import limpar_dict_para_json
from app.models.ClienteModel import ClienteModel
from app.models.ContatoModel import ContatoModel
from app.models.ContratoModel import ContratoModel
from app.models.EnderecoModel import EnderecoModel
from app.models.LogModel import LogModel
from sqlalchemy import or_, func, cast, Date, and_
from sqlalchemy.orm import joinedload
from app.schemas.ClienteSchema import ClienteResponse, ClienteContratoResponse
from app.schemas.ContatoSchema import ContatoResponse, PaginatedContatosResponse, ContatoRequest
from app.schemas.ContratoSchema import ContratoResponse
from app.schemas.EnderecoSchema import EnderecoRequest
from sqlalchemy.future import select

from app.schemas.ParcelamentoSchema import ParcelamentoResponse


async def por_contrato_id(
        contrato_id: uuid.UUID,
        pagina: int = Query(1, ge=1),
        items: int = Query(10, ge=1, le=15000),
        db: AsyncSession = Depends(get_db)
):
    offset = (pagina - 1) * items

    query = select(ContratoModel).options(
        joinedload(ContratoModel.parcelamento),
        joinedload(ContratoModel.responsavel_assinatura),
        joinedload(ContratoModel.cliente_assinatura),
        joinedload(ContratoModel.cliente),
        joinedload(ContratoModel.vendedor),
    ).where(ContratoModel.id == contrato_id)

    result = await db.execute(query)
    contrato = result.scalar_one_or_none()
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

    contratoInfo = ContratoResponse(
        id=contrato.id,
        numero=contrato.numero,
        nome=contrato.nome,
        documento=contrato.documento,
        ativo=contrato.ativo,
        status_cobranca=contrato.status_cobranca,
        status_contrato=contrato.status_contrato,
        parcelamento=parcelamento,
        cliente=cliente,
        created_at=contrato.created_at,
        updated_at=contrato.updated_at,
        deleted_at=contrato.deleted_at,
        created_by=contrato.created_by,
        updated_by=contrato.updated_by,
        deleted_by=contrato.deleted_by,
    )

    where_clause = [ContatoModel.contrato_id == contrato_id]

    total_query = select(func.count(ContatoModel.id)).where(*where_clause)
    total_result = await db.execute(total_query)
    total_items = total_result.scalar()

    total_paginas = (total_items + items - 1) // items if total_items > 0 else 0

    query = (
        select(ContatoModel)
        .where(*where_clause)
        .offset(offset)
        .limit(items)
    )
    result = await db.execute(query)
    contatos = result.scalars().unique().all()

    contatos_list = []
    for contato in contatos:
        contatos_response = ContatoResponse(
            id=contato.id,
            meio=contato.meio,
            data_hora=contato.data_hora,
            valor=contato.valor,
            descricao=contato.descricao,
            status=contato.status,
            created_at=contato.created_at,
            created_by=contato.created_by,
            efetivo=contato.efetivo,
        )
        contatos_list.append(contatos_response)

    page = PaginatedContatosResponse(
        total_items=total_items,
        contrato=contratoInfo,
        total_paginas=total_paginas,
        pagina_atual=pagina,
        items=items,
        offset=offset,
        data=contatos_list
    )

    return page

async def por_id(id: uuid.UUID, cliente: ClienteResponse,
                      db: AsyncSession = Depends(get_db)):
    where_clause = [ContatoModel.id == id]

    query = (
        select(ContatoModel)
        .where(*where_clause)
    )

    result = await db.execute(query)
    contato = result.scalars().first()

    if contato:
        contato_response = ContatoResponse(
            id=contato.id,
            meio=contato.meio,
            data_hora=contato.data_hora,
            valor=contato.valor,
            descricao=contato.descricao,
            status=contato.status,
            created_at=contato.created_at,
            created_by=contato.created_by,
            efetivo=contato.efetivo,
        )

    return contato_response


async def criar(form_data: ContatoRequest,
                     db: AsyncSession = Depends(get_db), user_id: str = Depends(verificar_token)):

    form_data.id = uuid.uuid4()

    novo_contato = ContatoModel(
        id=form_data.id,
        meio =form_data.meio,
        contrato_id = form_data.contrato_id,
        usuario_id = uuid.UUID(user_id),
        cliente_id = form_data.cliente_id,
        data_hora = form_data.data_hora,
        valor = form_data.valor,
        efetivo = form_data.efetivo,
        descricao = form_data.descricao,
        status = form_data.status,
        created_at = form_data.created_at,
        created_by = uuid.UUID(user_id)
    )

    db.add(novo_contato)

    dados_antigos = None
    dados_novos = limpar_dict_para_json(form_data)

    log = LogModel(
        tabela_afetada="contatos",
        operacao="CREATE",
        registro_id=form_data.id,
        dados_antes=dados_antigos,
        dados_depois=dados_novos,
        usuario_id=uuid.UUID(user_id)
    )

    db.add(log)

    await db.commit()
    await db.refresh(novo_contato)

    return JSONResponse(
        content={"detail": "Contato realizado com sucesso"},
        media_type="application/json; charset=utf-8"
    )



