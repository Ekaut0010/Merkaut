from pydantic import BaseModel, Field


class ProdutoCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=150)
    preco: float = Field(gt=0)
    codigo_de_barras: str = Field(min_length=1, max_length=50)


class ProdutoUpdate(BaseModel):
    nome: str = Field(min_length=2, max_length=150)
    preco: float = Field(gt=0)
    codigo_de_barras: str = Field(min_length=1, max_length=50)