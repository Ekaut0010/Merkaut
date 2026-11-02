import os
import psycopg2
from app.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME


def get_conexao():
    ambiente_teste = os.getenv("TESTING") == "1"

    nome_banco = "merkaut_test" if ambiente_teste else DB_NAME

    conexao = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=nome_banco
    )

    return conexao