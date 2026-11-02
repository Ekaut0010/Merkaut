import os
import psycopg2
from fastapi import FastAPI
from pydantic import BaseModel # Ferramenta nova para criar o molde dos dados
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="API do Merkaut")

def get_conexao():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dbname=os.getenv("DB_NAME")
    )

# 1. Criamos o molde exato do que a API espera receber
class MercadoCreate(BaseModel):
    nome: str

@app.get("/")
def ler_raiz():
    return {"mensagem": "O servidor do Merkaut está online!"}

@app.get("/teste-db")
def testar_banco():
    try:
        conn = get_conexao()
        conn.close()
        return {"mensagem": "Conexão com o banco de dados realizada com sucesso! 🗄️"}
    except Exception as e:
        return {"erro": f"Falha ao conectar: {e}"}

# 2. Nova rota POST que recebe o molde e grava na base de dados
@app.post("/mercados", status_code=201)
def criar_mercado(mercado: MercadoCreate):
    conn = get_conexao()
    cursor = conn.cursor()
    try:
        # Comando SQL INSERT. O %s é usado por segurança contra ataques cibernéticos (SQL Injection)
        cursor.execute(
            "INSERT INTO Mercados (nome) VALUES (%s) RETURNING id, nome;",
            (mercado.nome,)
        )
        novo_mercado = cursor.fetchone()
        conn.commit() # Executa a ordem de guardar definitivamente no cofre
        
        return {"id": novo_mercado[0], "nome": novo_mercado[1]}
    except Exception as e:
        conn.rollback() # Se der erro, desfaz qualquer tentativa incompleta
        return {"erro": f"Falha ao criar mercado: {e}"}
    finally:
        cursor.close()
        conn.close()

# 3. Rota GET para listar todos os mercados cadastrados
@app.get("/mercados")
def listar_mercados():
    conn = get_conexao()
    cursor = conn.cursor()
    try:
        # Comando SQL SELECT para buscar todos os registros
        cursor.execute("SELECT id, nome FROM Mercados;")
        linhas = cursor.fetchall() # Pega todos os resultados que o banco encontrou
        
        # Converte as linhas do banco em uma lista organizada para devolver na tela
        lista_mercados = [{"id": linha[0], "nome": linha[1]} for linha in linhas]
        return lista_mercados
    except Exception as e:
        return {"erro": f"Falha ao listar mercados: {e}"}
    finally:
        cursor.close()
        conn.close()

# 4. Molde exato do que a API espera receber para um Produto
class ProdutoCreate(BaseModel):
    nome: str
    preco: float
    codigo_de_barras: str
    mercado_id: int # É aqui que garantimos a que mercado o produto pertence!

# 5. Rota POST para registar um produto novo
@app.post("/produtos", status_code=201)
def criar_produto(produto: ProdutoCreate):
    conn = get_conexao()
    cursor = conn.cursor()
    try:
        # Inserimos os 4 dados na tabela Produtos
        cursor.execute(
            """
            INSERT INTO Produtos (nome, preco, codigo_de_barras, mercado_id) 
            VALUES (%s, %s, %s, %s) RETURNING id, nome;
            """,
            (produto.nome, produto.preco, produto.codigo_de_barras, produto.mercado_id)
        )
        novo_produto = cursor.fetchone()
        conn.commit()
        
        return {
            "id": novo_produto[0], 
            "nome": novo_produto[1],
            "mensagem": "Produto registado e vinculado ao mercado com sucesso!"
        }
    except Exception as e:
        conn.rollback()
        # Se tentarmos usar um mercado_id que não existe, o banco de dados vai disparar um erro aqui
        return {"erro": f"Falha ao criar produto: {e}"}
    finally:
        cursor.close()
        conn.close()

# 6. Rota GET para listar os produtos isolados de um mercado específico
@app.get("/mercados/{mercado_id}/produtos")
def listar_produtos_do_mercado(mercado_id: int):
    conn = get_conexao()
    cursor = conn.cursor()
    try:
        # O WHERE é o escudo do nosso SaaS: filtra para trazer apenas os produtos daquele mercado
        cursor.execute(
            "SELECT id, nome, preco, codigo_de_barras FROM Produtos WHERE mercado_id = %s;",
            (mercado_id,)
        )
        linhas = cursor.fetchall() 
        
        # Monta a lista organizada para o ecrã
        lista_produtos = [
            {"id": l[0], "nome": l[1], "preco": l[2], "codigo_de_barras": l[3]} 
            for l in linhas
        ]
        return lista_produtos
    except Exception as e:
        return {"erro": f"Falha ao listar produtos: {e}"}
    finally:
        cursor.close()
        conn.close()