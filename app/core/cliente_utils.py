import uuid
from typing import Optional

from fastapi import Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from starlette import status
from starlette.responses import JSONResponse

from app.connection.database import get_db
from app.core.auth_utils import verificar_token
from app.core.log_utils import limpar_dict_para_json
from app.models.ClienteModel import ClienteModel
from app.models.EnderecoModel import EnderecoModel
from app.models.LogModel import LogModel
from sqlalchemy import or_, func, cast, Date
from sqlalchemy.orm import joinedload
from app.schemas.ClienteSchema import ClienteResponse, PaginatedClienteResponse, ClienteRequest, ClienteUpdate
from app.schemas.EnderecoSchema import EnderecoRequest
from sqlalchemy.future import select



async def listar(
        pagina: int = Query(1, ge=1),
        items: int = Query(10, ge=1, le=15000),
        buscar: Optional[str] = Query(None),
        data_cadastro: Optional[datetime] = Query(None),
        ativo: Optional[bool] = Query(None),
        db: AsyncSession = Depends(get_db)
):
    offset = (pagina - 1) * items

    where_clause = [ClienteModel.deleted_at == None]

    if(ativo != None):
        where_clause.append(ClienteModel.ativo == ativo)

    if buscar:
        filtro_str = f"%{buscar.lower()}%"
        where_clause.append(
            or_(
                func.lower(ClienteModel.nome).ilike(filtro_str),
                func.lower(ClienteModel.documento).ilike(filtro_str),
            )
        )

    if data_cadastro:
        where_clause.append(
            cast(ClienteModel.created_at, Date) == data_cadastro.date()
        )

    total_query = select(func.count(ClienteModel.id)).where(*where_clause)
    total_result = await db.execute(total_query)
    total_items = total_result.scalar()

    total_paginas = (total_items + items - 1) // items if total_items > 0 else 0

    query = (
        select(ClienteModel)
        .options(joinedload(ClienteModel.endereco))
        .where(*where_clause)
        .offset(offset)
        .limit(items)
    )
    result = await db.execute(query)
    clientes = result.scalars().unique().all()

    cliente_list = []
    for cliente in clientes:
        endereco = None
        if cliente.endereco:
            endereco = EnderecoRequest(
                id=cliente.endereco.id,
                cep=cliente.endereco.cep,
                rua=cliente.endereco.rua,
                numero=cliente.endereco.numero,
                bairro=cliente.endereco.bairro,
                complemento=cliente.endereco.complemento,
                cidade=cliente.endereco.cidade,
                uf=cliente.endereco.uf
            )

        cliente_response = ClienteResponse(
            id=cliente.id,
            nome=cliente.nome,
            documento=cliente.documento,
            email=cliente.email,
            telefone=cliente.telefone,
            grupo_segmento=cliente.grupo_segmento,
            ativo=cliente.ativo,
            created_at=cliente.created_at,
            updated_at=cliente.updated_at,
            deleted_at=cliente.deleted_at,
            created_by=cliente.created_by,
            updated_by=cliente.updated_by,
            deleted_by=cliente.deleted_by,
            endereco=endereco,
        )

        cliente_list.append(cliente_response)

    page = PaginatedClienteResponse(
        total_items=total_items,
        total_paginas=total_paginas,
        pagina_atual=pagina,
        items=items,
        offset=offset,
        data=cliente_list
    )

    return page

async def listar_por_id(id: uuid.UUID, cliente: ClienteResponse,
                      db: AsyncSession = Depends(get_db)):
    queryEndereco = select(EnderecoModel).where(EnderecoModel.id == cliente.endereco_id)
    resultEndereco = await db.execute(queryEndereco)
    clienteEndereco = resultEndereco.scalar_one_or_none()

    endereco = None

    if clienteEndereco:
        endereco = EnderecoRequest(
            id=clienteEndereco.id,
            cep=clienteEndereco.cep,
            rua=clienteEndereco.rua,
            numero=clienteEndereco.numero,
            bairro=clienteEndereco.bairro,
            complemento=clienteEndereco.complemento,
            cidade=clienteEndereco.cidade,
            uf=clienteEndereco.uf
        )

    queryEnderecoComercial = select(EnderecoModel).where(EnderecoModel.id == cliente.endereco_comercial_id)
    resultEnderecoComercial = await db.execute(queryEnderecoComercial)
    clienteEnderecoComercial = resultEnderecoComercial.scalar_one_or_none()

    endereco_comercial = None

    if clienteEnderecoComercial:
        endereco_comercial = EnderecoRequest(
            id=clienteEnderecoComercial.id,
            cep=clienteEnderecoComercial.cep,
            rua=clienteEnderecoComercial.rua,
            numero=clienteEnderecoComercial.numero,
            bairro=clienteEnderecoComercial.bairro,
            complemento=clienteEnderecoComercial.complemento,
            cidade=clienteEnderecoComercial.cidade,
            uf=clienteEnderecoComercial.uf
        )

    cliente = ClienteResponse(
        id=id,
        nome=cliente.nome,
        documento=cliente.documento,
        email=cliente.email,
        telefone=cliente.telefone,
        grupo_segmento=cliente.grupo_segmento,
        ativo=cliente.ativo,
        created_at=cliente.created_at,
        updated_at=cliente.updated_at,
        deleted_at=cliente.deleted_at,
        created_by=cliente.created_by,
        updated_by=cliente.updated_by,
        deleted_by=cliente.deleted_by,
        endereco=endereco,
        endereco_comercial=endereco_comercial,
    )

    return cliente




async def criar(form_data: ClienteRequest,
                     db: AsyncSession = Depends(get_db), user_id: str = Depends(verificar_token)):
    endereco_id = None
    if form_data.endereco:
        endereco_data = form_data.endereco
        novo_endereco = EnderecoModel(
            id=uuid.uuid4(),
            cep=endereco_data.cep,
            rua=endereco_data.rua,
            numero=endereco_data.numero,
            bairro=endereco_data.bairro,
            complemento=endereco_data.complemento,
            cidade=endereco_data.cidade,
            uf=endereco_data.uf
        )
        db.add(novo_endereco)
        await db.flush()
        endereco_id = novo_endereco.id

    endereco_comercial_id = None
    if form_data.endereco_comercial:
        endereco_comercial_data = form_data.endereco_comercial
        novo_endereco_comercial = EnderecoModel(
            id=uuid.uuid4(),
            cep=endereco_comercial_data.cep,
            rua=endereco_comercial_data.rua,
            numero=endereco_comercial_data.numero,
            bairro=endereco_comercial_data.bairro,
            complemento=endereco_comercial_data.complemento,
            cidade=endereco_comercial_data.cidade,
            uf=endereco_comercial_data.uf
        )
        db.add(novo_endereco_comercial)
        await db.flush()
        endereco_comercial_id = novo_endereco_comercial.id

    form_data.id = uuid.uuid4()

    novo_cliente = ClienteModel(
        id=form_data.id,
        endereco_id=endereco_id,
        endereco_comercial_id=endereco_comercial_id,
        nome=form_data.nome,
        documento=form_data.documento,
        email=form_data.email,
        telefone=form_data.telefone,
        ativo=True,
        grupo_segmento=form_data.grupo_segmento,
        created_by= uuid.UUID(user_id)
    )

    db.add(novo_cliente)

    dados_antigos = None
    dados_novos = limpar_dict_para_json(form_data)

    log = LogModel(
        tabela_afetada="clientes",
        operacao="CREATE",
        registro_id=form_data.id,
        dados_antes=dados_antigos,
        dados_depois=dados_novos,
        usuario_id=uuid.UUID(user_id)
    )

    db.add(log)

    await db.commit()
    await db.refresh(novo_cliente)

    return JSONResponse(
        content={"detail": "Cliente criado com sucesso"},
        media_type="application/json; charset=utf-8"
    )



async def atualizar(id: uuid.UUID, form_data: ClienteUpdate,
                         db: AsyncSession = Depends(get_db), user_id: str = Depends(verificar_token)):
    result = await db.execute(select(ClienteModel).where(ClienteModel.id == id))
    cliente = result.scalar_one_or_none()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )

    dados_antigos = limpar_dict_para_json(cliente)

    cliente.updated_by = uuid.UUID(user_id)

    if form_data.nome is not None:
        cliente.nome = form_data.nome
    if form_data.documento is not None:
        cliente.documento = form_data.documento
    if form_data.email is not None:
        cliente.email = form_data.email
    if form_data.telefone is not None:
        cliente.telefone = form_data.telefone
    if form_data.grupo_segmento is not None:
        cliente.grupo_segmento = form_data.grupo_segmento


    if form_data.endereco:
        if cliente.endereco_id:
            result = await db.execute(select(EnderecoModel).where(EnderecoModel.id == cliente.endereco_id))
            endereco = result.scalar_one_or_none()
        else:
            endereco = EnderecoModel(id=uuid.uuid4())
            db.add(endereco)
            cliente.endereco_id = endereco.id

        endereco_data = form_data.endereco

        if endereco_data.cep is not None:
            endereco.cep = endereco_data.cep
        if endereco_data.rua is not None:
            endereco.rua = endereco_data.rua
        if endereco_data.numero is not None:
            endereco.numero = endereco_data.numero
        if endereco_data.bairro is not None:
            endereco.bairro = endereco_data.bairro
        if endereco_data.complemento is not None:
            endereco.complemento = endereco_data.complemento
        if endereco_data.cidade is not None:
            endereco.cidade = endereco_data.cidade
        if endereco_data.uf is not None:
            endereco.uf = endereco_data.uf

        db.add(endereco)

    if form_data.endereco_comercial:
        if cliente.endereco_comercial_id:
            result = await db.execute(select(EnderecoModel).where(EnderecoModel.id == cliente.endereco_comercial_id))
            endereco_comercial = result.scalar_one_or_none()
        else:
            endereco_comercial = EnderecoModel(id=uuid.uuid4())
            db.add(endereco_comercial)
            cliente.endereco_comercial_id = endereco_comercial.id

        endereco_data_comercial = form_data.endereco_comercial

        if endereco_data_comercial.cep is not None:
            endereco_comercial.cep = endereco_data_comercial.cep
        if endereco_data_comercial.rua is not None:
            endereco_comercial.rua = endereco_data_comercial.rua
        if endereco_data_comercial.numero is not None:
            endereco_comercial.numero = endereco_data_comercial.numero
        if endereco_data_comercial.bairro is not None:
            endereco_comercial.bairro = endereco_data_comercial.bairro
        if endereco_data_comercial.complemento is not None:
            endereco_comercial.complemento = endereco_data_comercial.complemento
        if endereco_data_comercial.cidade is not None:
            endereco_comercial.cidade = endereco_data_comercial.cidade
        if endereco_data_comercial.uf is not None:
            endereco_comercial.uf = endereco_data_comercial.uf

        db.add(endereco_comercial)

    dados_novos = limpar_dict_para_json(cliente)
    log = LogModel(
        tabela_afetada="clientes",
        operacao="UPDATE",
        registro_id=cliente.id,
        dados_antes=dados_antigos,
        dados_depois=dados_novos,
        usuario_id=uuid.UUID(user_id)
    )

    db.add(log)

    await db.commit()
    await db.refresh(cliente)

    return JSONResponse(
        content={"detail": "Cliente atualizado com sucesso"},
        media_type="application/json; charset=utf-8"
    )



