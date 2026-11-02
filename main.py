from fastapi import FastAPI

from app.routes import mercados, auth, produtos


# Inicialização da API
app = FastAPI(
    title="Merkaut API",
    description="Sistema de gerenciamento de estoque para mercados.",
    version="1.0.0"
)


# Registro das rotas
app.include_router(mercados.router)
app.include_router(auth.router)
app.include_router(produtos.router)


# Rota principal
@app.get("/")
def ler_raiz():
    return {
        "mensagem": "O servidor do Merkaut está online!",
        "versao": "1.0.0"
    }