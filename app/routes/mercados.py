from fastapi import APIRouter, HTTPException
import psycopg2

from app.database import get_conexao
from app.schemas.mercado import MercadoCreate
from app.security.auth import obter_hash_senha


router = APIRouter(
    prefix="/mercados",
    tags=["Mercados"]
)


@router.post("/", status_code=201)
def criar_mercado(mercado: MercadoCreate):

    conn = get_conexao()
    cursor = conn.cursor()

    try:
        senha_hash = obter_hash_senha(mercado.senha)

        cursor.execute(
            """
            INSERT INTO Mercados (nome, email, senha)
            VALUES (%s, %s, %s)
            RETURNING id, nome, email;
            """,
            (mercado.nome, mercado.email, senha_hash)
        )

        novo_mercado = cursor.fetchone()
        conn.commit()

        return {
            "id": novo_mercado[0],
            "nome": novo_mercado[1],
            "email": novo_mercado[2],
            "mensagem": "Mercado cadastrado com sucesso!"
        }

    except psycopg2.errors.UniqueViolation:
        conn.rollback()

        raise HTTPException(
            status_code=409,
            detail="Este email já está cadastrado."
        )

    except Exception:
        conn.rollback()

        raise HTTPException(
            status_code=500,
            detail="Erro interno ao cadastrar mercado."
        )

    finally:
        cursor.close()
        conn.close()