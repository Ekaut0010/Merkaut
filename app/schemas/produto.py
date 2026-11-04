from typing import Literal
from pydantic import BaseModel, Field


class ProdutoCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=150)
    preco: float = Field(gt=0)
    unidade_medida: Literal["UN", "KG", "G", "L", "M"] = "UN"
    codigo_de_barras: str | None = Field(default=None, max_length=50)
    quantidade_estoque: float = Field(ge=0)
    estoque_minimo: float = Field(ge=0)
    categoria: Literal[
    "Hortifruti",
    "Açougue",
    "Limpeza",
    "Higiene",
    "Beleza",
    "Eletrônicos",
    "Diversos"
] = "Diversos"


class ProdutoUpdate(BaseModel):
    nome: str = Field(min_length=2, max_length=150)
    preco: float = Field(gt=0)
    unidade_medida: Literal["UN", "KG", "G", "L", "M"] = "UN"
    codigo_de_barras: str | None = Field(default=None, max_length=50)
    quantidade_estoque: float = Field(ge=0)
    estoque_minimo: float = Field(ge=0)
    categoria: Literal[
        "Hortifruti",
        "Açougue",
        "Limpeza",
        "Higiene",
        "Beleza",
        "Eletrônicos",
        "Diversos"
    ] = "Diversos"