import uuid
from datetime import datetime
from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse

from app.connection.database import get_db
from app.core.auth_utils import verificar_token
from app.core.log_utils import limpar_dict_para_json
from app.models.LogModel import LogModel
from sqlalchemy import func, and_

from app.models.PlanoModel import PlanoModel
from app.models.ServicoModel import ServicoModel
from sqlalchemy.future import select

from app.schemas.ServicoSchema import ServicoBase, ServicoRequest, ServicoUpdate, ServicoList


async def listar(
    pagina: int = Query(1, ge=1),
    items: int = Query(10, ge=1, le=100),
    filtro: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    offset = (pagina - 1) * items

    where_clause = [ServicoModel.deleted_at == None]
    if filtro:
        filtro_str = f"%{filtro.lower()}%"
        where_clause.append(func.lower(ServicoModel.nome).ilike(filtro_str))

    total_query = select(func.count(ServicoModel.id)).where(*where_clause)
    total_result = await db.execute(total_query)
    total_items = total_result.scalar()

    total_paginas = (total_items + items - 1) // items if total_items > 0 else 0

    query = (
        select(ServicoModel)
        .where(*where_clause)
        .offset(offset)
        .limit(items)
    )
    result = await db.execute(query)
    servicos = result.scalars().unique().all()

    servico_list = []
    for servico in servicos:
        servico_response = ServicoBase(
            id=servico.id,
            nome=servico.nome,
            descricao=servico.descricao,
            valor=servico.valor,
            ativo=servico.ativo,
            categoria=servico.categoria,
            created_by=servico.created_by,
            updated_by=servico.updated_by,
            deleted_by=servico.deleted_by,
            created_at=servico.created_at,
            updated_at=servico.updated_at,
            deleted_at=servico.deleted_at
        )
        servico_list.append(servico_response)

    return {
        "total_items": total_items,
        "total_paginas": total_paginas,
        "pagina_atual": pagina,
        "items": items,
        "offset": offset,
        "data": servico_list
    }


async def listagem_simples(
    pagina: int = Query(1, ge=1),
    items: int = Query(10, ge=1, le=10000),
    filtro: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    offset = (pagina - 1) * items

    where_clause = [ServicoModel.ativo == True]
    if filtro:
        filtro_str = f"%{filtro.lower()}%"
        where_clause.append(func.lower(ServicoModel.nome).ilike(filtro_str))

    total_query = select(func.count(ServicoModel.id)).where(*where_clause)
    total_result = await db.execute(total_query)
    total_items = total_result.scalar()

    total_paginas = (total_items + items - 1) // items if total_items > 0 else 0

    query = (
        select(ServicoModel)
        .where(*where_clause)
        .offset(offset)
        .limit(items)
    )
    result = await db.execute(query)
    servicos = result.scalars().unique().all()

    servico_list = []
    for servico in servicos:
        servico_response = ServicoList(
            id=servico.id,
            nome=servico.nome,
            valor=servico.valor,
            categoria=servico.categoria
        )
        servico_list.append(servico_response)

    return {
        "total_items": total_items,
        "total_paginas": total_paginas,
        "pagina_atual": pagina,
        "items": items,
        "offset": offset,
        "data": servico_list
    }



async def por_id(id: uuid.UUID,
                   db: AsyncSession = Depends(get_db)):

    query = select(ServicoModel).where(ServicoModel.id == id)
    result = await db.execute(query)
    servico = result.scalar_one_or_none()
    if not servico:
        raise HTTPException(status_code=400, detail="Serviço não localizado na base de dados.")

    return servico



async def criar(form_data: ServicoRequest,
                     db: AsyncSession = Depends(get_db), user_id: str = Depends(verificar_token)):

    queryNome = select(ServicoModel).where(ServicoModel.nome == form_data.nome)
    resultNome = await db.execute(queryNome)
    servicoNome = resultNome.scalar_one_or_none()

    if form_data.nome is None:
        raise HTTPException(status_code=400, detail=f"Insira o nome.")

    if not form_data.nome:
        raise HTTPException(status_code=400, detail=f"Insira o nome.")

    if servicoNome:
        raise HTTPException(status_code=400, detail=f"Este Nome já está vinculado a um serviço existente.")

    form_data.id = uuid.uuid4()

    if not form_data.valor:
        raise HTTPException(status_code=400, detail=f"Insira o valor!")

    if form_data.valor <= 0:
        raise HTTPException(status_code=400, detail=f"Valor deve ser positivo!")

    novo_servico = ServicoModel(
        id=form_data.id,
        nome=form_data.nome,
        descricao=form_data.descricao,
        valor=form_data.valor,
        categoria=form_data.categoria,
        ativo=True,
        created_by=uuid.UUID(user_id)
    )

    db.add(novo_servico)

    dados_antigos = None
    dados_novos =  limpar_dict_para_json(form_data)

    log = LogModel(
        tabela_afetada="servicos",
        operacao="CREATE",
        registro_id=form_data.id,
        dados_antes=dados_antigos,
        dados_depois=dados_novos,
        usuario_id=uuid.UUID(user_id)
    )

    db.add(log)

    await db.commit()
    await db.refresh(novo_servico)

    return JSONResponse(
        content={"detail": "Serviço criado com sucesso"},
        media_type="application/json; charset=utf-8"
    )



async def atualizar(id: uuid.UUID, form_data: ServicoUpdate,
                   db: AsyncSession = Depends(get_db), user_id: str = Depends(verificar_token)):

    query = select(ServicoModel).where(ServicoModel.id == id)
    result = await db.execute(query)
    servico = result.scalar_one_or_none()
    if not servico:
        raise HTTPException(status_code=400, detail="Serviço não localizado na base de dados.")

    if form_data.nome is None:
        raise HTTPException(status_code=400, detail=f"Insira o nome.")

    if form_data.nome:
        queryNome = select(ServicoModel).where(
            and_(
                ServicoModel.nome == form_data.nome,
                ServicoModel.ativo == True,
                ServicoModel.id != id,
            )
        )
        resultNome = await db.execute(queryNome)
        servicoNome = resultNome.scalar_one_or_none()
        if servicoNome:
            raise HTTPException(status_code=400,
                                detail=f"Este Nome já está vinculado a um Serviço existente.")

    if form_data.valor is not None:
        if form_data.valor <= 0:
            raise HTTPException(status_code=400, detail=f"Valor deve ser positivo!")

    result = await db.execute(select(ServicoModel).where(ServicoModel.id == id))
    servico = result.scalar_one_or_none()
    if not servico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Serviço não encontrado"
        )

    dados_antigos = limpar_dict_para_json(servico)
    servico.updated_by = uuid.UUID(user_id)

    if form_data.nome is not None:
        servico.nome = form_data.nome
    if form_data.descricao is not None:
        servico.descricao = form_data.descricao
    if form_data.valor is not None:
        servico.valor = form_data.valor
    if form_data.categoria is not None:
        servico.categoria = form_data.categoria
    if form_data.ativo is not None:
        servico.ativo = form_data.ativo

    dados_novos =  limpar_dict_para_json(servico)
    log = LogModel(
        tabela_afetada="servicos",
        operacao="UPDATE",
        registro_id=servico.id,
        dados_antes=dados_antigos,
        dados_depois=dados_novos,
        usuario_id=uuid.UUID(user_id)
    )

    db.add(log)

    await db.commit()
    await db.refresh(servico)

    return JSONResponse(
        content={"detail": "Serviço atualizado com sucesso"},
        media_type="application/json; charset=utf-8"
    )



async def delete(id: UUID, db: AsyncSession = Depends(get_db), user_id: str = Depends(verificar_token)):

    query = select(ServicoModel).where(ServicoModel.id == id)
    result = await db.execute(query)
    servico = result.scalar_one_or_none()

    if not servico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Serviço não encontrado."
        )

    query = select(PlanoModel).where(
        and_(
            PlanoModel.servicos_vinculados.any(id),
            PlanoModel.ativo == True
        ))
    result = await db.execute(query)
    planos = result.scalar_one_or_none()

    if planos:
        dados_antigos = limpar_dict_para_json(servico)
        servico.updated_at = datetime.utcnow()
        servico.updated_by = uuid.UUID(user_id)
        servico.ativo = False
        dados_novos = limpar_dict_para_json(servico)

        log = LogModel(
            tabela_afetada="servicos",
            operacao="UPDATE",
            registro_id=servico.id,
            dados_antes=dados_antigos,
            dados_depois=dados_novos,
            usuario_id=uuid.UUID(user_id)
        )

        db.add(log)
        await db.commit()

        return JSONResponse(
            content={"detail": "Serviço está vinculado a um plano e não pode ser excluído! Foi inativado com sucesso!"},
            media_type="application/json; charset=utf-8"
        )

    dados_antigos = limpar_dict_para_json(servico)

    servico.ativo = False
    servico.deleted_at = datetime.utcnow()
    servico.deleted_by = uuid.UUID(user_id)

    dados_novos = limpar_dict_para_json(servico)

    log = LogModel(
        tabela_afetada="servicos",
        operacao="DELETE",
        registro_id=servico.id,
        dados_antes=dados_antigos,
        dados_depois=dados_novos,
        usuario_id=uuid.UUID(user_id)
    )

    db.add(log)
    await db.commit()

    return JSONResponse(
        content={"detail": "Serviço deletado com sucesso"},
        media_type="application/json; charset=utf-8"
    )
