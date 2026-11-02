from fastapi import APIRouter, HTTPException, Depends

from app.database import get_conexao
from app.schemas.produto import ProdutoCreate, ProdutoUpdate
from app.security.auth import obter_mercado_atual


router = APIRouter(
    prefix="/produtos",
    tags=["Produtos"]
)


# LISTAR PRODUTOS
@router.get("/")
def listar_produtos(
    mercado_id: int = Depends(obter_mercado_atual)
):

    conn = get_conexao()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT id, nome, preco, codigo_de_barras
            FROM Produtos
            WHERE mercado_id = %s;
            """,
            (mercado_id,)
        )

        produtos = cursor.fetchall()

        return [
            {
                "id": p[0],
                "nome": p[1],
                "preco": p[2],
                "codigo_de_barras": p[3]
            }
            for p in produtos
        ]

    finally:
        cursor.close()
        conn.close()


# CADASTRAR PRODUTO
@router.post("/", status_code=201)
def criar_produto(
    produto: ProdutoCreate,
    mercado_id: int = Depends(obter_mercado_atual)
):

    conn = get_conexao()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO Produtos
            (nome, preco, codigo_de_barras, mercado_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id, nome;
            """,
            (
                produto.nome,
                produto.preco,
                produto.codigo_de_barras,
                mercado_id
            )
        )

        novo_produto = cursor.fetchone()
        conn.commit()

        return {
            "id": novo_produto[0],
            "nome": novo_produto[1],
            "mensagem": "Produto cadastrado com sucesso!"
        }

    except Exception:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erro ao cadastrar produto."
        )

    finally:
        cursor.close()
        conn.close()


# ATUALIZAR PRODUTO
@router.put("/{produto_id}")
def atualizar_produto(
    produto_id: int,
    produto: ProdutoUpdate,
    mercado_id: int = Depends(obter_mercado_atual)
):

    conn = get_conexao()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE Produtos
            SET nome = %s,
                preco = %s,
                codigo_de_barras = %s
            WHERE id = %s
            AND mercado_id = %s
            RETURNING id, nome;
            """,
            (
                produto.nome,
                produto.preco,
                produto.codigo_de_barras,
                produto_id,
                mercado_id
            )
        )

        atualizado = cursor.fetchone()

        if atualizado is None:
            raise HTTPException(
                status_code=404,
                detail="Produto não encontrado."
            )

        conn.commit()

        return {
            "mensagem": f"Produto '{atualizado[1]}' atualizado!"
        }

    finally:
        cursor.close()
        conn.close()


# EXCLUIR PRODUTO
@router.delete("/{produto_id}")
def deletar_produto(
    produto_id: int,
    mercado_id: int = Depends(obter_mercado_atual)
):

    conn = get_conexao()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            DELETE FROM Produtos
            WHERE id = %s
            AND mercado_id = %s
            RETURNING id;
            """,
            (produto_id, mercado_id)
        )

        deletado = cursor.fetchone()

        if deletado is None:
            raise HTTPException(
                status_code=404,
                detail="Produto não encontrado."
            )

        conn.commit()

        return {
            "mensagem": "Produto excluído com sucesso!"
        }

    finally:
        cursor.close()
        conn.close()