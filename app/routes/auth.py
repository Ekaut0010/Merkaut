from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.database import get_conexao
from app.security.auth import (
    verificar_senha,
    criar_token_acesso
)


router = APIRouter(tags=["Autenticação"])


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):

    conn = get_conexao()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT id, nome, senha
            FROM Mercados
            WHERE email = %s;
            """,
            (form_data.username,)
        )

        mercado = cursor.fetchone()

        if not mercado or not verificar_senha(
            form_data.password,
            mercado[2]
        ):
            raise HTTPException(
                status_code=401,
                detail="Email ou senha incorretos."
            )

        token = criar_token_acesso(
            mercado_id=mercado[0],
            nome=mercado[1]
        )

        return {
            "access_token": token,
            "token_type": "bearer"
        }

    finally:
        cursor.close()
        conn.close()