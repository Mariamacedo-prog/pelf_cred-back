import uuid
from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from sqlalchemy.orm import joinedload
from starlette import status
from starlette.responses import JSONResponse
from sqlalchemy.sql import delete
from app.Enum.StatusContrato import StatusContrato
from app.Enum.StatusCobranca import StatusCobranca
from app.connection.database import get_db
from app.core.anexo_utils import base64_to_bytes, bytes_to_base64
from app.core.auth_utils import verificar_token
from app.core.log_utils import limpar_dict_para_json
from app.models.ContratoModel import ContratoModel
from app.models.ClienteModel import ClienteModel
from app.models.AnexoModel import AnexoModel
from app.models.LogModel import LogModel
from app.models.ParcelamentoModel import ParcelamentoModel
from app.models.PlanoModel import PlanoModel
from sqlalchemy import func, and_, or_, cast, String

from app.models.VendedorModel import VendedorModel
from app.schemas.AnexoSchema import AnexoRequest
from app.schemas.ClienteSchema import ClienteResponse, ClienteContratoResponse
from app.schemas.ContratoSchema import ContratoRequest, ContratoResponse
from app.schemas.EnderecoSchema import EnderecoRequest
from app.schemas.ParcelamentoSchema import ParcelamentoResponse
from app.schemas.PlanoSchema import PlanoBase, PlanoUpdate, PlanoRequest
from sqlalchemy.future import select

from app.schemas.VendedorSchema import VendedorContratoResponse


async def criar(form_data: ContratoRequest,
                     db: AsyncSession = Depends(get_db), user_id: str = Depends(verificar_token)):

    queryPlano = select(ContratoModel).where(
        and_(
                ContratoModel.cliente_id == form_data.cliente_id,
                ContratoModel.ativo == True,
                ContratoModel.plano_id == form_data.plano_id,
        )
    )
    resultPlano = await db.execute(queryPlano)
    contratoPlano = resultPlano.scalar_one_or_none()
    if contratoPlano:
        raise HTTPException(status_code=400, detail=f"Já existe um contrato ativo para este cliente com o mesmo plano selecionado.")

    form_data.id = uuid.uuid4()

    if not form_data.cliente_id:
        raise HTTPException(status_code=400, detail=f"Cliente inválido, tente novamente!")

    queryClienteId = select(ClienteModel).where(
        and_(
            ClienteModel.id == form_data.cliente_id,
            ClienteModel.ativo == True
        )
    )
    resultClienteId = await db.execute(queryClienteId)
    contratoClienteId = resultClienteId.scalar_one_or_none()
    if not contratoClienteId:
        raise HTTPException(status_code=400, detail=f"Cliente não localizado ou inativo, verifique os dados e tente novamente.")


    if not form_data.plano_id:
        raise HTTPException(status_code=400, detail=f"Plano inválido, tente novamente!")

    queryPlanoId = select(PlanoModel).where(
        and_(
            PlanoModel.id == form_data.plano_id,
            PlanoModel.ativo == True
        )
    )
    resultPlanoId = await db.execute(queryPlanoId)
    contratoPlanoId = resultPlanoId.scalar_one_or_none()
    if not contratoPlanoId:
        raise HTTPException(status_code=400,
                            detail=f"Plano não localizado ou inativo, verifique os dados e tente novamente.")


    if form_data.vendedor_id is not None:
        queryVendedorId = select(VendedorModel).where(
            and_(
                VendedorModel.id == form_data.vendedor_id,
                VendedorModel.ativo == True
            )
        )
        resultVendedorId = await db.execute(queryVendedorId)
        contratoVendedorId = resultVendedorId.scalar_one_or_none()
        if not contratoVendedorId:
            raise HTTPException(status_code=400,
                                detail=f"Vendedor não localizado ou inativo, verifique os dados e tente novamente.")



    if not form_data.parcelamento.data_inicio:
        raise HTTPException(status_code=400, detail=f"Por favor, escolha a data de início.")


    if form_data.parcelamento.valor_total <= 0 or form_data.parcelamento.valor_parcela <= 0:
        raise HTTPException(
            status_code=400,
            detail="O valor total e o valor da parcela devem ser maiores que zero."
        )




    anexos_id = []
    if form_data.anexos_list is not None:
        for anexo in form_data.anexos_list:
            image_bytes = base64_to_bytes(anexo.base64)
            novo_anexo = AnexoModel(
                id=uuid.uuid4(),
                base64=image_bytes,
                image=anexo.image,
                descricao=anexo.descricao,
                nome=anexo.nome,
                tipo=anexo.tipo,
                created_by=uuid.UUID(user_id)
            )
            db.add(novo_anexo)
            await db.flush()
            anexos_id.append(novo_anexo.id)

    parcelamento_id = uuid.uuid4()
    novo_parcelamento = ParcelamentoModel(
        id=parcelamento_id,
        contrato_id=form_data.id,
        data_inicio= form_data.parcelamento.data_inicio,
        data_fim= form_data.parcelamento.data_fim,
        data_vigencia= form_data.parcelamento.data_vigencia,
        meio_pagamento= form_data.parcelamento.meio_pagamento,
        valor_total= form_data.parcelamento.valor_total,
        valor_parcela= form_data.parcelamento.valor_parcela,
        valor_entrada= form_data.parcelamento.valor_entrada,
        qtd_parcela= form_data.parcelamento.qtd_parcela,
        avista= form_data.parcelamento.avista,
        taxa_juros= form_data.parcelamento.taxa_juros,
        data_ultimo_pagamento= form_data.parcelamento.data_ultimo_pagamento,
        qtd_parcelas_pagas= form_data.parcelamento.qtd_parcelas_pagas,
        ativo=True,
        created_by=uuid.UUID(user_id)
    )
    db.add(novo_parcelamento)
    await db.flush()

    novo_contrato = ContratoModel(
        id=form_data.id,
        parcelamento_id=parcelamento_id,
        cliente_assinatura_id=None,
        responsavel_assinatura_id=None,
        cliente_id=form_data.cliente_id,
        vendedor_id=form_data.vendedor_id,
        plano_id=form_data.plano_id,
        anexos_list_id=anexos_id,
        servicos_list_id=None,
        nome=contratoClienteId.nome,
        documento=contratoClienteId.documento,
        status_cobranca=StatusCobranca.EM_DIA.value,
        status_contrato=StatusContrato.INICIADO.value,
        ativo=True,
        created_by=uuid.UUID(user_id)
    )
    db.add(novo_contrato)
    await db.flush()

    dados_antigos = None
    dados_novos =  limpar_dict_para_json(form_data)

    log = LogModel(
        tabela_afetada="contratos",
        operacao="CREATE",
        registro_id=form_data.id,
        dados_antes=dados_antigos,
        dados_depois=dados_novos,
        usuario_id=uuid.UUID(user_id)
    )

    db.add(log)

    await db.commit()
    await db.refresh(novo_contrato)

    return JSONResponse(
        content={"detail": "Contrato criado com sucesso"},
        media_type="application/json; charset=utf-8"
    )



async def listar(
    pagina: int = Query(1, ge=1),
    items: int = Query(10, ge=1, le=100),
    filtro: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    offset = (pagina - 1) * items

    where_clause = [ContratoModel.deleted_at == None]

    total_query = select(func.count(ContratoModel.id))

    if filtro:
        filtro_str = f"%{filtro.lower()}%"
        where_clause.append(
            or_(
                func.lower(cast(ContratoModel.numero, String)).ilike(filtro_str),
                func.lower(ContratoModel.status_contrato).ilike(filtro_str),
                func.lower(ClienteModel.nome).ilike(filtro_str),
                func.lower(cast(ClienteModel.documento, String)).ilike(filtro_str)
            )
        )
        total_query = total_query.join(ClienteModel, ContratoModel.cliente_id == ClienteModel.id)


    total_query = total_query.where(*where_clause)
    total_result = await db.execute(total_query)
    total_items = total_result.scalar()
    total_paginas = (total_items + items - 1) // items if total_items > 0 else 0

    query = select(ContratoModel).options(
        joinedload(ContratoModel.parcelamento),
        joinedload(ContratoModel.responsavel_assinatura),
        joinedload(ContratoModel.cliente_assinatura),
        joinedload(ContratoModel.cliente),
        joinedload(ContratoModel.vendedor),
        joinedload(ContratoModel.plano),
    )

    if filtro:
        query = query.join(ClienteModel, ContratoModel.cliente_id == ClienteModel.id)

    query = query.where(*where_clause).offset(offset).limit(items)

    result = await db.execute(query)
    contratos = result.scalars().unique().all()

    contratos_list = []
    for contrato in contratos:
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

                created_at = contrato.parcelamento.created_at,
                updated_at = contrato.parcelamento.updated_at,
                deleted_at=contrato.parcelamento.deleted_at,
                created_by=contrato.parcelamento.created_by,
                updated_by=contrato.parcelamento.updated_by,
                deleted_by=contrato.parcelamento.deleted_by,
            )

        anexo_list = []
        if contrato.anexos_list_id:
            for anexo_id in contrato.anexos_list_id:
                query = select(AnexoModel).where(
                    and_(
                        AnexoModel.id == anexo_id
                    )
                )
                result = await db.execute(query)
                item = result.scalar_one_or_none()

                if item:
                    image_base64 = bytes_to_base64(item.base64, item.tipo)
                    anexo = AnexoRequest(
                        id=item.id,
                        image=item.image,
                        base64=image_base64,
                        descricao=item.descricao,
                        nome=item.nome,
                        tipo=item.tipo,
                    )
                    anexo_list.append(anexo)

        cliente_assinatura = None
        if contrato.cliente_assinatura:
            image_base64 = bytes_to_base64(contrato.cliente_assinatura.base64, contrato.cliente_assinatura.tipo)
            cliente_assinatura = AnexoRequest(
                id=contrato.cliente_assinatura.id,
                image=contrato.cliente_assinatura.image,
                base64=image_base64,
                descricao=contrato.cliente_assinatura.descricao,
                nome=contrato.cliente_assinatura.nome,
                tipo=contrato.cliente_assinatura.tipo,
            )

        responsavel_assinatura = None
        if contrato.responsavel_assinatura:
            image_base64 = bytes_to_base64(contrato.responsavel_assinatura.base64, contrato.responsavel_assinatura.tipo)
            responsavel_assinatura = AnexoRequest(
                id=contrato.responsavel_assinatura.id,
                image=contrato.responsavel_assinatura.image,
                base64=image_base64,
                descricao=contrato.responsavel_assinatura.descricao,
                nome=contrato.responsavel_assinatura.nome,
                tipo=contrato.responsavel_assinatura.tipo,
            )

        cliente = None
        if contrato.cliente:
            cliente = ClienteContratoResponse(
                id=contrato.cliente.id,
                nome=contrato.cliente.nome,
                documento=contrato.cliente.documento,
                email=contrato.cliente.email,
                telefone=contrato.cliente.telefone,
                grupo_segmento=contrato.cliente.grupo_segmento,
                ativo=contrato.cliente.ativo
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

        plano = None
        if contrato.plano:
            plano = PlanoRequest(
                id=contrato.plano.id,
                nome=contrato.plano.nome,
                descricao=contrato.plano.descricao,
                valor_mensal=contrato.plano.valor_mensal,
                numero_parcelas=contrato.plano.numero_parcelas,
                avista=contrato.plano.avista,
                periodo_vigencia=contrato.plano.periodo_vigencia,
                servicos_vinculados=contrato.plano.servicos_vinculados
            )

        response = ContratoResponse(
            id=contrato.id,
            numero=contrato.numero,
            nome=contrato.nome,
            documento=contrato.documento,
            ativo=contrato.ativo,
            status_cobranca=contrato.status_cobranca,
            status_contrato=contrato.status_contrato,

            parcelamento=parcelamento,
            cliente_assinatura=cliente_assinatura,
            responsavel_assinatura=responsavel_assinatura,
            anexos_list=anexo_list,
            plano=plano,
            vendedor=vendedor,
            cliente=cliente,

            created_by=contrato.created_by,
            updated_by=contrato.updated_by,
            deleted_by=contrato.deleted_by,
            created_at=contrato.created_at,
            updated_at=contrato.updated_at,
            deleted_at=contrato.deleted_at,
        )
        contratos_list.append(response)

    return {
        "total_items": total_items,
        "total_paginas": total_paginas,
        "pagina_atual": pagina,
        "items": items,
        "offset": offset,
        "data": contratos_list
    }

async def por_id(id: uuid.UUID,
                   db: AsyncSession = Depends(get_db)):

    query = select(ContratoModel).options(
        joinedload(ContratoModel.parcelamento),
        joinedload(ContratoModel.responsavel_assinatura),
        joinedload(ContratoModel.cliente_assinatura),
        joinedload(ContratoModel.cliente),
        joinedload(ContratoModel.vendedor),
        joinedload(ContratoModel.plano),
    ).where(ContratoModel.id == id)

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

            created_at=contrato.parcelamento.created_at,
            updated_at=contrato.parcelamento.updated_at,
            deleted_at=contrato.parcelamento.deleted_at,
            created_by=contrato.parcelamento.created_by,
            updated_by=contrato.parcelamento.updated_by,
            deleted_by=contrato.parcelamento.deleted_by,
        )

    anexo_list = []
    if contrato.anexos_list_id:
        for anexo_id in contrato.anexos_list_id:
            query = select(AnexoModel).where(
                and_(
                    AnexoModel.id == anexo_id
                )
            )
            result = await db.execute(query)
            item = result.scalar_one_or_none()

            if item:
                image_base64 = bytes_to_base64(item.base64, item.tipo)
                anexo = AnexoRequest(
                    id=item.id,
                    image=item.image,
                    base64=image_base64,
                    descricao=item.descricao,
                    nome=item.nome,
                    tipo=item.tipo,
                )
                anexo_list.append(anexo)

    cliente_assinatura = None
    if contrato.cliente_assinatura:
        image_base64 = bytes_to_base64(contrato.cliente_assinatura.base64, contrato.cliente_assinatura.tipo)
        cliente_assinatura = AnexoRequest(
            id=contrato.cliente_assinatura.id,
            image=contrato.cliente_assinatura.image,
            base64=image_base64,
            descricao=contrato.cliente_assinatura.descricao,
            nome=contrato.cliente_assinatura.nome,
            tipo=contrato.cliente_assinatura.tipo,
        )

    responsavel_assinatura = None
    if contrato.responsavel_assinatura:
        image_base64 = bytes_to_base64(contrato.responsavel_assinatura.base64, contrato.responsavel_assinatura.tipo)
        responsavel_assinatura = AnexoRequest(
            id=contrato.responsavel_assinatura.id,
            image=contrato.responsavel_assinatura.image,
            base64=image_base64,
            descricao=contrato.responsavel_assinatura.descricao,
            nome=contrato.responsavel_assinatura.nome,
            tipo=contrato.responsavel_assinatura.tipo,
        )

    cliente = None
    if contrato.cliente:
        cliente = ClienteContratoResponse(
            id=contrato.cliente.id,
            nome=contrato.cliente.nome,
            documento=contrato.cliente.documento,
            email=contrato.cliente.email,
            telefone=contrato.cliente.telefone,
            grupo_segmento=contrato.cliente.grupo_segmento,
            ativo=contrato.cliente.ativo
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

    plano = None
    if contrato.plano:
        plano = PlanoRequest(
            id=contrato.plano.id,
            nome=contrato.plano.nome,
            descricao=contrato.plano.descricao,
            valor_mensal=contrato.plano.valor_mensal,
            numero_parcelas=contrato.plano.numero_parcelas,
            avista=contrato.plano.avista,
            periodo_vigencia=contrato.plano.periodo_vigencia,
            servicos_vinculados=contrato.plano.servicos_vinculados
        )

    response = ContratoResponse(
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
        plano=plano,
        anexos_list=anexo_list,
        responsavel_assinatura=responsavel_assinatura,
        cliente_assinatura=cliente_assinatura,
        created_at=contrato.created_at,
        updated_at=contrato.updated_at,
        deleted_at=contrato.deleted_at,
        created_by=contrato.created_by,
        updated_by=contrato.updated_by,
        deleted_by=contrato.deleted_by,
    )

    return response



async def atualizar(id: uuid.UUID, form_data: PlanoUpdate,
                   db: AsyncSession = Depends(get_db), user_id: str = Depends(verificar_token)):
    queryContrato = select(ContratoModel).where(ContratoModel.id == id)
    resultContrato = await db.execute(queryContrato)
    contrato_existente = resultContrato.scalar_one_or_none()

    dados_antes = limpar_dict_para_json(contrato_existente)

    if not contrato_existente:
        raise HTTPException(status_code=404, detail="Contrato não encontrado.")

    queryPlanoDuplicado = select(ContratoModel).where(
        and_(
            ContratoModel.cliente_id == form_data.cliente_id,
            ContratoModel.plano_id == form_data.plano_id,
            ContratoModel.ativo == True,
            ContratoModel.id != id
        )
    )
    resultPlanoDuplicado = await db.execute(queryPlanoDuplicado)
    if resultPlanoDuplicado.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Já existe um contrato ativo para este cliente com o mesmo plano."
        )

    queryCliente = select(ClienteModel).where(
        and_(
            ClienteModel.id == form_data.cliente_id,
            ClienteModel.ativo == True
        )
    )
    resultCliente = await db.execute(queryCliente)
    cliente = resultCliente.scalar_one_or_none()
    if not cliente:
        raise HTTPException(status_code=400, detail="Cliente não localizado ou inativo.")

    queryPlano = select(PlanoModel).where(
        and_(
            PlanoModel.id == form_data.plano_id,
            PlanoModel.ativo == True
        )
    )
    resultPlano = await db.execute(queryPlano)
    plano = resultPlano.scalar_one_or_none()
    if not plano:
        raise HTTPException(status_code=400, detail="Plano não localizado ou inativo.")

    if form_data.vendedor_id:
        queryVendedor = select(VendedorModel).where(
            and_(
                VendedorModel.id == form_data.vendedor_id,
                VendedorModel.ativo == True
            )
        )
        resultVendedor = await db.execute(queryVendedor)
        vendedor = resultVendedor.scalar_one_or_none()
        if not vendedor:
            raise HTTPException(status_code=400, detail="Vendedor não localizado ou inativo.")

    if not form_data.parcelamento.data_inicio:
        raise HTTPException(status_code=400, detail="Data de início obrigatória.")

    if form_data.parcelamento.valor_total <= 0 or form_data.parcelamento.valor_parcela <= 0:
        raise HTTPException(
            status_code=400,
            detail="O valor total e o valor da parcela devem ser maiores que zero."
        )

    anexos_antigos_ids = set(contrato_existente.anexos_list_id or [])
    anexos_novos_ids = set()
    anexos_final_ids = []

    if form_data.anexos_list:
        for anexo in form_data.anexos_list:
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

                    db.merge(anexo_existente)

                    anexos_novos_ids.add(anexo.id)
                    anexos_final_ids.append(anexo.id)
            else:
                image_bytes = base64_to_bytes(anexo.base64)
                novo_anexo = AnexoModel(
                    id=uuid.uuid4(),
                    base64=image_bytes,
                    image=anexo.image,
                    descricao=anexo.descricao,
                    nome=anexo.nome,
                    tipo=anexo.tipo,
                    created_by=uuid.UUID(user_id)
                )
                db.add(novo_anexo)
                await db.flush()
                anexos_final_ids.append(novo_anexo.id)

    anexos_para_apagar = anexos_antigos_ids - anexos_novos_ids
    if anexos_para_apagar:
        delete_query = delete(AnexoModel).where(AnexoModel.id.in_(anexos_para_apagar))
        await db.execute(delete_query)

    parcelamento_id = None
    if form_data.parcelamento.id:
        query_parcelamento_existente = select(ParcelamentoModel).where(ParcelamentoModel.id == form_data.parcelamento.id)
        result_parcelamento = await db.execute(query_parcelamento_existente)
        parcelamento_existente = result_parcelamento.scalar_one_or_none()

        parcelamento_id = form_data.parcelamento.id
        if parcelamento_existente:
            if parcelamento_existente.data_inicio is not None:
                parcelamento_existente.data_inicio = form_data.parcelamento.data_inicio
            if parcelamento_existente.data_fim is not None:
                parcelamento_existente.data_fim = form_data.parcelamento.data_fim
            if parcelamento_existente.data_vigencia is not None:
                parcelamento_existente.data_vigencia = form_data.parcelamento.data_vigencia
            if parcelamento_existente.meio_pagamento is not None:
                parcelamento_existente.meio_pagamento = form_data.parcelamento.meio_pagamento
            if parcelamento_existente.valor_total is not None:
                parcelamento_existente.valor_total = form_data.parcelamento.valor_total
            if parcelamento_existente.valor_parcela is not None:
                parcelamento_existente.valor_parcela = form_data.parcelamento.valor_parcela
            if parcelamento_existente.valor_entrada is not None:
                parcelamento_existente.valor_entrada = form_data.parcelamento.valor_entrada
            if parcelamento_existente.qtd_parcela is not None:
                parcelamento_existente.qtd_parcela = form_data.parcelamento.qtd_parcela
            if parcelamento_existente.avista is not None:
                parcelamento_existente.avista = form_data.parcelamento.avista
            if parcelamento_existente.taxa_juros is not None:
                parcelamento_existente.taxa_juros = form_data.parcelamento.taxa_juros
            if parcelamento_existente.data_ultimo_pagamento is not None:
                parcelamento_existente.data_ultimo_pagamento = form_data.parcelamento.data_ultimo_pagamento
            if parcelamento_existente.qtd_parcelas_pagas is not None:
                parcelamento_existente.qtd_parcelas_pagas = form_data.parcelamento.qtd_parcelas_pagas
            parcelamento_existente.updated_by = uuid.UUID(user_id)
            parcelamento_existente.updated_at = datetime.utcnow()

            db.merge(parcelamento_existente)
    else:
        novo_parcelamento_id = uuid.uuid4()
        novo_parcelamento = ParcelamentoModel(
            id=novo_parcelamento_id,
            contrato_id=form_data.id,
            data_inicio=form_data.parcelamento.data_inicio,
            data_fim=form_data.parcelamento.data_fim,
            data_vigencia=form_data.parcelamento.data_vigencia,
            meio_pagamento=form_data.parcelamento.meio_pagamento,
            valor_total=form_data.parcelamento.valor_total,
            valor_parcela=form_data.parcelamento.valor_parcela,
            valor_entrada=form_data.parcelamento.valor_entrada,
            qtd_parcela=form_data.parcelamento.qtd_parcela,
            avista=form_data.parcelamento.avista,
            taxa_juros=form_data.parcelamento.taxa_juros,
            data_ultimo_pagamento=form_data.parcelamento.data_ultimo_pagamento,
            qtd_parcelas_pagas=form_data.parcelamento.qtd_parcelas_pagas,
            ativo=True,
            created_by=uuid.UUID(user_id)
        )
        db.add(novo_parcelamento)
        await db.flush()
        parcelamento_id = novo_parcelamento_id

    contrato_existente.updated_at = datetime.utcnow()
    contrato_existente.parcelamento_id = parcelamento_id
    contrato_existente.cliente_id = form_data.cliente_id
    contrato_existente.vendedor_id = form_data.vendedor_id
    contrato_existente.plano_id = form_data.plano_id
    contrato_existente.anexos_list_id = anexos_final_ids
    contrato_existente.nome = cliente.nome
    contrato_existente.documento = cliente.documento
    contrato_existente.updated_by = uuid.UUID(user_id)

    dados_depois = limpar_dict_para_json(form_data)

    log = LogModel(
        tabela_afetada="contratos",
        operacao="UPDATE",
        registro_id=form_data.id,
        dados_antes=dados_antes,
        dados_depois=dados_depois,
        usuario_id=uuid.UUID(user_id)
    )
    db.add(log)

    await db.commit()
    await db.refresh(contrato_existente)

    return JSONResponse(
        content={"detail": "Contrato atualizado com sucesso"},
        media_type="application/json; charset=utf-8"
    )


async def delete_item(id: UUID, db: AsyncSession = Depends(get_db), user_id: str = Depends(verificar_token)):

    query = select(ContratoModel).where(ContratoModel.id == id)
    result = await db.execute(query)
    contrato = result.scalar_one_or_none()

    if not contrato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contrato não encontrado."
        )

    dados_antigos = limpar_dict_para_json(contrato)

    contrato.ativo = False
    contrato.deleted_at = datetime.utcnow()
    contrato.deleted_by = uuid.UUID(user_id)

    dados_novos = limpar_dict_para_json(contrato)

    log = LogModel(
        tabela_afetada="contratos",
        operacao="DELETE",
        registro_id=contrato.id,
        dados_antes=dados_antigos,
        dados_depois=dados_novos,
        usuario_id=uuid.UUID(user_id)
    )

    db.add(log)
    await db.commit()

    return JSONResponse(
        content={"detail": "Contrato deletado com sucesso"},
        media_type="application/json; charset=utf-8"
    )




