from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import mercados, auth, produtos


# Inicialização da API
app = FastAPI(
    title="Merkaut API",
    description="Sistema de gerenciamento de estoque para mercados.",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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