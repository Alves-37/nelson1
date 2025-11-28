from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from app.db.database import get_db_session
from app.db.models import Abastecimento, ItemAbastecimento, Produto, User
from app.schemas.abastecimento import (
    AbastecimentoCreate,
    AbastecimentoResponse,
)


router = APIRouter(prefix="/api/abastecimentos", tags=["abastecimentos"])


def _parse_uuid(value: str, field: str) -> uuid.UUID:
    try:
        return uuid.UUID(value)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"{field} inválido")


async def _get_usuario(db: AsyncSession, usuario_id: str | None) -> User | None:
    if not usuario_id:
        return None
    usuario_uuid = _parse_uuid(usuario_id, "usuario_id")
    result = await db.execute(select(User).where(User.id == usuario_uuid, User.ativo == True))
    return result.scalar_one_or_none()


@router.get("/", response_model=List[AbastecimentoResponse])
async def listar_abastecimentos(db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(Abastecimento).order_by(Abastecimento.created_at.desc()))
    abastecimentos = result.scalars().all()
    return [AbastecimentoResponse.model_validate(a) for a in abastecimentos]


@router.get("/{abastecimento_id}", response_model=AbastecimentoResponse)
async def obter_abastecimento(abastecimento_id: str, db: AsyncSession = Depends(get_db_session)):
    uuid_obj = _parse_uuid(abastecimento_id, "abastecimento_id")
    result = await db.execute(select(Abastecimento).where(Abastecimento.id == uuid_obj))
    abastecimento = result.scalar_one_or_none()
    if not abastecimento:
        raise HTTPException(status_code=404, detail="Abastecimento não encontrado")
    return AbastecimentoResponse.model_validate(abastecimento)


@router.post("/", response_model=AbastecimentoResponse, status_code=201)
async def criar_abastecimento(payload: AbastecimentoCreate, db: AsyncSession = Depends(get_db_session)):
    usuario = await _get_usuario(db, payload.usuario_id)
    if payload.usuario_id and not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado ou inativo")

    if not payload.itens:
        raise HTTPException(status_code=400, detail="É necessário informar pelo menos um item")

    abastecimento = Abastecimento(
        fornecedor_nome=payload.fornecedor_nome,
        fornecedor_id=payload.fornecedor_id,
        usuario_id=usuario.id if usuario else None,
        observacoes=payload.observacoes,
    )
    db.add(abastecimento)
    await db.flush()

    total = 0.0
    for item in payload.itens:
        produto_uuid = _parse_uuid(item.produto_id, "produto_id")
        result = await db.execute(select(Produto).where(Produto.id == produto_uuid))
        produto = result.scalar_one_or_none()
        if not produto:
            raise HTTPException(status_code=404, detail=f"Produto não encontrado: {item.produto_id}")

        quantidade = float(item.quantidade)
        preco_custo = float(item.preco_custo)
        preco_venda = float(item.preco_venda) if item.preco_venda is not None else None
        subtotal = quantidade * preco_custo
        total += subtotal

        novo_item = ItemAbastecimento(
            abastecimento_id=abastecimento.id,
            produto_id=produto.id,
            quantidade=quantidade,
            preco_custo=preco_custo,
            preco_venda=preco_venda,
            subtotal=subtotal,
        )
        db.add(novo_item)

        produto.estoque = (produto.estoque or 0) + quantidade
        produto.preco_custo = preco_custo
        if preco_venda is not None:
            produto.preco_venda = preco_venda

    abastecimento.total = total

    await db.commit()
    await db.refresh(abastecimento)
    return AbastecimentoResponse.model_validate(abastecimento)
