from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
import uuid


class ItemAbastecimentoBase(BaseModel):
    produto_id: str
    quantidade: float = Field(..., gt=0)
    preco_custo: float = Field(..., ge=0)
    preco_venda: Optional[float] = Field(default=None, ge=0)


class ItemAbastecimentoCreate(ItemAbastecimentoBase):
    pass


class ItemAbastecimentoResponse(ItemAbastecimentoBase):
    id: str
    subtotal: float
    created_at: datetime
    updated_at: datetime

    @field_validator("id", "produto_id", mode="before")
    @classmethod
    def uuid_to_str(cls, value):
        if isinstance(value, uuid.UUID):
            return str(value)
        return value

    class Config:
        from_attributes = True


class AbastecimentoBase(BaseModel):
    fornecedor_nome: Optional[str] = None
    fornecedor_id: Optional[str] = None
    usuario_id: Optional[str] = None
    observacoes: Optional[str] = None


class AbastecimentoCreate(AbastecimentoBase):
    itens: List[ItemAbastecimentoCreate] = Field(default_factory=list)


class AbastecimentoResponse(AbastecimentoBase):
    id: str
    total: float
    created_at: datetime
    updated_at: datetime
    itens: List[ItemAbastecimentoResponse] = Field(default_factory=list)
    usuario_nome: Optional[str] = None

    @field_validator("id", "usuario_id", mode="before")
    @classmethod
    def uuid_to_str(cls, value):
        if isinstance(value, uuid.UUID):
            return str(value)
        return value

    class Config:
        from_attributes = True
