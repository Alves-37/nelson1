from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api/categorias", tags=["categorias"])


class CategoriaOut(BaseModel):
    id: int
    nome: str
    descricao: str | None = None


# Lista padrão alinhada com o cliente PDV3 (database.py),
# mantendo os mesmos IDs, nomes e descrições.
CATEGORIAS_PADRAO: List[CategoriaOut] = [
    CategoriaOut(id=1, nome="Acessórios Diversos", descricao="Suportes, anéis e outros acessórios para telemóveis"),
    CategoriaOut(id=2, nome="Cabos e Carregadores", descricao="Cabos, carregadores e adaptadores"),
    CategoriaOut(id=3, nome="Capas e Películas", descricao="Capas, películas e proteções para telemóveis"),
    CategoriaOut(id=4, nome="Elétrica", descricao="Materiais elétricos"),
    CategoriaOut(id=5, nome="Encadernação e Acabamento", descricao="Encadernação, plastificação e outros acabamentos"),
    CategoriaOut(id=6, nome="Ferragem Geral", descricao="Demais itens de ferragem"),
    CategoriaOut(id=7, nome="Ferramentas", descricao="Ferramentas em geral"),
    CategoriaOut(id=8, nome="Fones e Áudio", descricao="Fones de ouvido e dispositivos de áudio"),
    CategoriaOut(id=9, nome="Hidráulica", descricao="Materiais hidráulicos"),
    CategoriaOut(id=10, nome="Impressão e Cópias", descricao="Serviços de impressão, cópias e digitalização"),
    CategoriaOut(id=11, nome="Insumos Internos", descricao="Papel, toner e insumos não vendidos diretamente"),
    CategoriaOut(id=12, nome="Papelaria", descricao="Cadernos, canetas, pastas e itens de papelaria"),
    CategoriaOut(id=13, nome="Parafusos e Fixadores", descricao="Parafusos, buchas, porcas, arruelas e fixadores"),
    CategoriaOut(id=14, nome="Gráfica", descricao="Serviços de gráfica, impressão especial, banners e materiais similares"),

    # Serviços gerais (sem controle de estoque)
    CategoriaOut(id=15, nome="Serviços", descricao="Serviços em geral sem controle de estoque"),
]


@router.get("/", response_model=List[CategoriaOut])
async def listar_categorias() -> List[CategoriaOut]:
    """
    Lista as categorias de produtos.

    Observação: Implementação sem dependência de banco para manter compatibilidade
    imediata com o cliente. Futuramente, pode ser migrado para uma tabela real
    quando o modelo `Categoria` existir no PostgreSQL.
    """
    return CATEGORIAS_PADRAO
