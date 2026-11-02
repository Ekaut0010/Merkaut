from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)


# Configuração de criptografia de senhas
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# Autenticação OAuth2
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/login"
)


# Gerar hash da senha
def obter_hash_senha(senha: str):
    return pwd_context.hash(senha)


# Verificar senha
def verificar_senha(senha_limpa: str, senha_hash: str):
    return pwd_context.verify(senha_limpa, senha_hash)


# Criar token JWT
def criar_token_acesso(mercado_id: int, nome: str):

    expiracao = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    dados_token = {
        "sub": str(mercado_id),
        "nome": nome,
        "exp": expiracao
    }

    token = jwt.encode(
        dados_token,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


# Identificar mercado autenticado
def obter_mercado_atual(token: str = Depends(oauth2_scheme)):

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        mercado_id = payload.get("sub")

        if mercado_id is None:
            raise InvalidTokenError("ID ausente")

        return int(mercado_id)

    except (InvalidTokenError, ValueError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Token inválido ou expirado. Faça login novamente.",
            headers={"WWW-Authenticate": "Bearer"}
        )