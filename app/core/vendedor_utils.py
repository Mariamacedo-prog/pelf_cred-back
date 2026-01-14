import uuid
from datetime import datetime
from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette import status
from starlette.responses import JSONResponse

from app.connection.database import get_db
from app.core.anexo_utils import base64_to_bytes, bytes_to_base64
from app.core.auth_utils import verificar_token
from app.core.log_utils import limpar_dict_para_json
from app.models.AnexoModel import AnexoModel
from app.models.EnderecoModel import EnderecoModel
from app.models.LogModel import LogModel
from sqlalchemy import func, and_, or_

from sqlalchemy.future import select

from app.models.VendedorModel import VendedorModel
from app.schemas.AnexoSchema import AnexoRequest
from app.schemas.EnderecoSchema import EnderecoRequest
from app.schemas.VendedorSchema import VendedorRequest, VendedorResponse, VendedorUpdate




async def listar(
    pagina: int = Query(1, ge=1),
    items: int = Query(10, ge=1, le=15000),
    filtro: Optional[str] = Query(None),
    filtro_cidade: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    offset = (pagina - 1) * items

    where_clause = [VendedorModel.deleted_at == None]

    if filtro:
        filtro_str = f"%{filtro.lower()}%"
        where_clause.append(
            or_(
                func.lower(VendedorModel.nome).ilike(filtro_str),
                func.lower(VendedorModel.cpf).ilike(filtro_str)
            )
        )

    if filtro_cidade:
        cidade_str = f"%{filtro_cidade.lower()}%"
        where_clause.append(func.lower(EnderecoModel.cidade).ilike(cidade_str))

    total_query = select(func.count(VendedorModel.id))
    if filtro_cidade:
        total_query = total_query.join(EnderecoModel, VendedorModel.endereco_id == EnderecoModel.id)
    total_query = total_query.where(*where_clause)

    total_result = await db.execute(total_query)
    total_items = total_result.scalar()
    total_paginas = (total_items + items - 1) // items if total_items > 0 else 0

    query = (
        select(VendedorModel)
        .join(EnderecoModel, VendedorModel.endereco_id == EnderecoModel.id)
        .options(
            joinedload(VendedorModel.endereco),
            joinedload(VendedorModel.foto),
        )
        .where(*where_clause)
        .offset(offset)
        .limit(items)
    )

    result = await db.execute(query)
    vendedores = result.scalars().unique().all()

    vendedores_list = []
    for vendedor in vendedores:
        endereco = None
        if vendedor.endereco:
            endereco = EnderecoRequest(
                id=vendedor.endereco.id,
                cep=vendedor.endereco.cep,
                rua=vendedor.endereco.rua,
                numero=vendedor.endereco.numero,
                bairro=vendedor.endereco.bairro,
                complemento=vendedor.endereco.complemento,
                cidade=vendedor.endereco.cidade,
                uf=vendedor.endereco.uf
            )

        anexo = None
        if vendedor.foto:
            image_base64 = bytes_to_base64(vendedor.foto.base64, vendedor.foto.tipo)
            anexo = AnexoRequest(
                id=vendedor.foto.id,
                image=vendedor.foto.image,
                base64=image_base64,
                descricao=vendedor.foto.descricao,
                nome=vendedor.foto.nome,
                tipo=vendedor.foto.tipo,
            )

        vendedor_response = VendedorResponse(
            id=vendedor.id,
            nome=vendedor.nome,
            comissao_pct=vendedor.comissao_pct,
            cpf=vendedor.cpf,
            rg=vendedor.rg,
            telefone=vendedor.telefone,
            email=vendedor.email,
            ativo=vendedor.ativo,
            created_by=vendedor.created_by,
            updated_by=vendedor.updated_by,
            deleted_by=vendedor.deleted_by,
            created_at=vendedor.created_at,
            updated_at=vendedor.updated_at,
            deleted_at=vendedor.deleted_at,
            endereco=endereco,
            foto=anexo
        )
        vendedores_list.append(vendedor_response)

    return {
        "total_items": total_items,
        "total_paginas": total_paginas,
        "pagina_atual": pagina,
        "items": items,
        "offset": offset,
        "data": vendedores_list
    }


async def por_id(id: uuid.UUID,
                   db: AsyncSession = Depends(get_db)):
    query = select(VendedorModel).where(VendedorModel.id == id)
    result = await db.execute(query)
    vendedor = result.scalar_one_or_none()

    if not vendedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendedor não encontrado."
        )

    queryEndereco = select(EnderecoModel).where(EnderecoModel.id == vendedor.endereco_id)
    resultEndereco = await db.execute(queryEndereco)
    vendedorEndereco = resultEndereco.scalar_one_or_none()

    endereco = None
    if vendedorEndereco:
        endereco = EnderecoRequest(
            id=vendedorEndereco.id,
            cep=vendedorEndereco.cep,
            rua=vendedorEndereco.rua,
            numero=vendedorEndereco.numero,
            bairro=vendedorEndereco.bairro,
            complemento=vendedorEndereco.complemento,
            cidade=vendedorEndereco.cidade,
            uf=vendedorEndereco.uf
        )

    foto = None
    if vendedor.foto_id:
        queryFoto = select(AnexoModel).where(AnexoModel.id == vendedor.foto_id)
        resultFoto = await db.execute(queryFoto)
        vendedorFoto = resultFoto.scalar_one_or_none()

        if vendedorFoto:
            image_base64 = bytes_to_base64(vendedorFoto.base64, vendedorFoto.tipo)
            foto = AnexoRequest(
                id=vendedorFoto.id,
                image=vendedorFoto.image,
                base64=image_base64,
                descricao=vendedorFoto.descricao,
                nome=vendedorFoto.nome,
                tipo=vendedorFoto.tipo
            )

    vendedor_response = VendedorResponse(
        id=vendedor.id,
        nome=vendedor.nome,
        cpf=vendedor.cpf,
        comissao_pct=vendedor.comissao_pct,
        rg=vendedor.rg,
        telefone=vendedor.telefone,
        email=vendedor.email,
        ativo=vendedor.ativo,
        created_by=vendedor.created_by,
        updated_by=vendedor.updated_by,
        deleted_by=vendedor.deleted_by,
        created_at=vendedor.created_at,
        updated_at=vendedor.updated_at,
        deleted_at=vendedor.deleted_at,
        endereco=endereco,
        foto=foto
    )

    return vendedor_response


async def criar(form_data: VendedorRequest,
                     db: AsyncSession = Depends(get_db), user_id: str = Depends(verificar_token)):

    querycpf = select(VendedorModel).where(VendedorModel.cpf == form_data.cpf)
    resultcpf = await db.execute(querycpf)
    vendedorcpf = resultcpf.scalar_one_or_none()

    if form_data.nome is None:
        raise HTTPException(status_code=400, detail=f"Campo nome é obrigatório.")

    if form_data.email is None:
        raise HTTPException(status_code=400, detail=f"Campo e-mail é obrigatório.")

    if form_data.telefone is None:
        raise HTTPException(status_code=400, detail=f"Campo telefone é obrigatório.")

    if form_data.cpf is None:
        raise HTTPException(status_code=400, detail=f"Campo CPD é obrigatório.")

    if vendedorcpf:
        raise HTTPException(status_code=400, detail=f"Este CPF já está vinculado a um vendedor existente.")

    form_data.id = uuid.uuid4()

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


    anexo_id = None
    if form_data.foto:
        image_bytes = base64_to_bytes(form_data.foto.base64)
        novo_anexo = AnexoModel(
            id=uuid.uuid4(),
            base64=image_bytes,
            image=form_data.foto.image,
            descricao=form_data.foto.descricao,
            nome=form_data.foto.nome,
            tipo=form_data.foto.tipo,
            created_by=uuid.UUID(user_id)
        )
        db.add(novo_anexo)
        await db.flush()
        anexo_id = novo_anexo.id


    novo = VendedorModel(
        id=form_data.id,
        comissao_pct=form_data.comissao_pct,
        nome=form_data.nome,
        cpf=form_data.cpf,
        rg=form_data.rg,
        telefone=form_data.telefone,
        email=form_data.email,
        ativo=True,
        foto_id=anexo_id,
        endereco_id=endereco_id,
        created_by=uuid.UUID(user_id)
    )

    db.add(novo)

    dados_antigos = None
    dados_novos =  limpar_dict_para_json(form_data)

    log = LogModel(
        tabela_afetada="vendedores",
        operacao="CREATE",
        registro_id=form_data.id,
        dados_antes=dados_antigos,
        dados_depois=dados_novos,
        usuario_id=uuid.UUID(user_id)
    )

    db.add(log)

    await db.commit()
    await db.refresh(novo)

    return JSONResponse(
        content={"detail": "Vendedor criado com sucesso"},
        media_type="application/json; charset=utf-8"
    )


async def atualizar(id: uuid.UUID, form_data: VendedorUpdate,
                   db: AsyncSession = Depends(get_db), user_id: str = Depends(verificar_token)):

    result = await db.execute(select(VendedorModel).where(VendedorModel.id == id))
    vendedor = result.scalar_one_or_none()
    if not vendedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendedor não encontrado"
        )

    if form_data.cpf:
        queryCpf = select(VendedorModel).where(
            and_(
                VendedorModel.cpf == form_data.cpf,
                VendedorModel.ativo == True,
                VendedorModel.id != id,
            )
        )
        resultCpf = await db.execute(queryCpf)
        vendedorCpf = resultCpf.scalar_one_or_none()
        if vendedorCpf:
            raise HTTPException(status_code=400, detail=f"Este CPF já está vinculado a um outro vendedor.")

    if form_data.email:
        queryEmail = select(VendedorModel).where(
            and_(
                VendedorModel.email == form_data.email,
                VendedorModel.ativo == True,
                VendedorModel.id != id,
            )
        )
        resultEmail = await db.execute(queryEmail)
        vendedorEmail = resultEmail.scalar_one_or_none()
        if vendedorEmail:
            raise HTTPException(status_code=400, detail=f"Este E-mail já está vinculado a um outro vendedor.")


    dados_antigos = limpar_dict_para_json(vendedor)
    vendedor.updated_by = uuid.UUID(user_id)

    if form_data.nome is not None:
        vendedor.nome = form_data.nome
    if form_data.cpf is not None:
        vendedor.cpf = form_data.cpf
    if form_data.email is not None:
        vendedor.email = form_data.email
    if form_data.telefone is not None:
        vendedor.telefone = form_data.telefone
    if form_data.rg is not None:
        vendedor.rg = form_data.rg
    if form_data.comissao_pct is not None:
        vendedor.comissao_pct = form_data.comissao_pct

    if form_data.endereco:
        if vendedor.endereco_id:
            result = await db.execute(select(EnderecoModel).where(EnderecoModel.id == vendedor.endereco_id))
            endereco = result.scalar_one_or_none()
        else:
            endereco = EnderecoModel(id=uuid.uuid4())
            db.add(endereco)
            vendedor.endereco_id = endereco.id

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


    if form_data.foto:
        if vendedor.foto_id:
            result = await db.execute(select(AnexoModel).where(AnexoModel.id == vendedor.foto_id))
            foto = result.scalar_one_or_none()
        else:
            foto = AnexoModel(id=uuid.uuid4())
            db.add(foto)
            vendedor.foto_id = foto.id

        foto_data_foto = form_data.foto

        if foto_data_foto.image is not None:
            foto.image = foto_data_foto.image
        if foto_data_foto.base64 is not None:
            image_bytes = base64_to_bytes(foto_data_foto.base64)
            foto.base64 = image_bytes
        if foto_data_foto.descricao is not None:
            foto.descricao = foto_data_foto.descricao
        if foto_data_foto.nome is not None:
            foto.nome = foto_data_foto.nome
        if foto_data_foto.tipo is not None:
            foto.tipo = foto_data_foto.tipo

        db.add(foto)


    dados_novos = limpar_dict_para_json(vendedor)
    log = LogModel(
        tabela_afetada="vendedores",
        operacao="UPDATE",
        registro_id=vendedor.id,
        dados_antes=dados_antigos,
        dados_depois=dados_novos,
        usuario_id=uuid.UUID(user_id)
    )

    db.add(log)

    await db.commit()
    await db.refresh(vendedor)

    return JSONResponse(
        content={"detail": "Vendedor atualizado com sucesso"},
        media_type="application/json; charset=utf-8"
    )


async def delete(id: UUID, db: AsyncSession = Depends(get_db), user_id: str = Depends(verificar_token)):

    query = select(VendedorModel).where(VendedorModel.id == id)
    result = await db.execute(query)
    vendedor = result.scalar_one_or_none()

    if not vendedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendedor não encontrado."
        )

    dados_antigos = limpar_dict_para_json(vendedor)

    vendedor.ativo = False
    vendedor.deleted_at = datetime.utcnow()
    vendedor.deleted_by = uuid.UUID(user_id)

    dados_novos = limpar_dict_para_json(vendedor)

    log = LogModel(
        tabela_afetada="vendedores",
        operacao="DELETE",
        registro_id=vendedor.id,
        dados_antes=dados_antigos,
        dados_depois=dados_novos,
        usuario_id=uuid.UUID(user_id)
    )

    db.add(log)
    await db.commit()

    return JSONResponse(
        content={"detail": "Vendedor deletado com sucesso"},
        media_type="application/json; charset=utf-8"
    )


