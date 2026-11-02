import os
import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field # O Field serve para colocar regras nos moldes
from dotenv import load_dotenv
from passlib.context import CryptContext # Ferramenta de segurança nova
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
import jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import PyJWTError

load_dotenv()

app = FastAPI(title="API do Merkaut")

# 1. Configura o "triturador" de palavras-passe usando o algoritmo bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def obter_hash_senha(senha):
    return pwd_context.hash(senha)

# Configurações do Crachá (Token)
SECRET_KEY = "chave_super_secreta_do_merkaut" 
ALGORITHM = "HS256"

# Avisa ao Swagger onde o usuário pega o crachá
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Função que intercepta o token na requisição e extrai o ID do mercado de forma segura
def obter_mercado_atual(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        mercado_id: str = payload.get("sub")
        if mercado_id is None:
            raise HTTPException(status_code=401, detail="Crachá inválido.")
        return int(mercado_id) # Devolve apenas o ID numérico do mercado
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Crachá inválido ou expirado. Faça login novamente.")
# Função que compara a senha que o usuário digitou com a que está no banco
def verificar_senha(senha_limpa, senha_encriptada):
    return pwd_context.verify(senha_limpa, senha_encriptada)

def get_conexao():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dbname=os.getenv("DB_NAME")
    )

# 2. O molde do Mercado agora exige email e senha com regras de tamanho
class MercadoCreate(BaseModel):
    nome: str
    email: str
    senha: str = Field(min_length=4, max_length=72) # Exige no mínimo 4 e no máximo 72 caracteres       

@app.get("/")
def ler_raiz():
    return {"mensagem": "O servidor do Merkaut está online!"}

# 3. Rota POST atualizada: agora ela encripta a senha antes de guardar!
@app.post("/mercados", status_code=201)
def criar_mercado(mercado: MercadoCreate):
    conn = get_conexao()
    cursor = conn.cursor()
    try:
        # Encripta a palavra-passe antes de a enviar para o PostgreSQL
        senha_encriptada = obter_hash_senha(mercado.senha)
        
        cursor.execute(
            "INSERT INTO Mercados (nome, email, senha) VALUES (%s, %s, %s) RETURNING id, nome, email;",
            (mercado.nome, mercado.email, senha_encriptada)
        )
        novo_mercado = cursor.fetchone()
        conn.commit()
        
        # Nunca devolvemos a senha (nem a encriptada) na resposta da API por segurança!
        return {"id": novo_mercado[0], "nome": novo_mercado[1], "email": novo_mercado[2]}
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        # Se o email já existir, o banco de dados avisa e nós devolvemos este erro amigável
        raise HTTPException(status_code=400, detail="Este email já está registado num mercado.")
    except Exception as e:
        conn.rollback()
        return {"erro": f"Falha ao criar mercado: {e}"}
    finally:
        cursor.close()
        conn.close()

# --- DAQUI PARA BAIXO É O CÓDIGO QUE JÁ TINHAS (Produtos e Listagens) ---

@app.get("/mercados")
def listar_mercados():
    conn = get_conexao()
    cursor = conn.cursor()
    try:
        # Adicionei o email na listagem para visualizarmos melhor
        cursor.execute("SELECT id, nome, email FROM Mercados;")
        linhas = cursor.fetchall()
        return [{"id": l[0], "nome": l[1], "email": l[2]} for l in linhas]
    except Exception as e:
        return {"erro": f"Falha ao listar mercados: {e}"}
    finally:
        cursor.close()
        conn.close()

# O molde do Produto NÃO pede mais o mercado_id! O sistema agora descobre sozinho.
class ProdutoCreate(BaseModel):
    nome: str
    preco: float
    codigo_de_barras: str

# Rota POST blindada: exige o crachá (Depends) antes de permitir a execução
@app.post("/produtos", status_code=201)
def criar_produto(produto: ProdutoCreate, mercado_id: int = Depends(obter_mercado_atual)):
    conn = get_conexao()
    cursor = conn.cursor()
    try:
        # Usamos o mercado_id que o nosso "Segurança" extraiu do Token JWT
        cursor.execute(
            "INSERT INTO Produtos (nome, preco, codigo_de_barras, mercado_id) VALUES (%s, %s, %s, %s) RETURNING id, nome;",
            (produto.nome, produto.preco, produto.codigo_de_barras, mercado_id) 
        )
        novo_produto = cursor.fetchone()
        conn.commit()
        return {"id": novo_produto[0], "nome": novo_produto[1], "mensagem": "Produto cadastrado com segurança!"}
    except Exception as e:
        conn.rollback()
        return {"erro": f"Falha ao criar produto: {e}"}
    finally:
        cursor.close()
        conn.close()

@app.get("/mercados/{mercado_id}/produtos")
def listar_produtos_do_mercado(mercado_id: int):
    conn = get_conexao()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, nome, preco, codigo_de_barras FROM Produtos WHERE mercado_id = %s;",
            (mercado_id,)
        )
        linhas = cursor.fetchall()
        return [{"id": l[0], "nome": l[1], "preco": l[2], "codigo_de_barras": l[3]} for l in linhas]
    except Exception as e:
        return {"erro": f"Falha ao listar produtos: {e}"}
    finally:
        cursor.close()
        conn.close()

class ProdutoUpdate(BaseModel):
    nome: str
    preco: float
    codigo_de_barras: str

@app.put("/produtos/{produto_id}")
def atualizar_produto(produto_id: int, produto: ProdutoUpdate):
    conn = get_conexao()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE Produtos SET nome = %s, preco = %s, codigo_de_barras = %s WHERE id = %s RETURNING id, nome;",
            (produto.nome, produto.preco, produto.codigo_de_barras, produto_id)
        )
        produto_atualizado = cursor.fetchone()
        conn.commit()
        if produto_atualizado is None:
            return {"erro": "Produto não encontrado."}
        return {"mensagem": f"Produto atualizado com sucesso!"}
    except Exception as e:
        conn.rollback()
        return {"erro": f"Falha ao atualizar produto: {e}"}
    finally:
        cursor.close()
        conn.close()

@app.delete("/produtos/{produto_id}")
def deletar_produto(produto_id: int):
    conn = get_conexao()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Produtos WHERE id = %s RETURNING id;", (produto_id,))
        produto_deletado = cursor.fetchone()
        conn.commit()
        if produto_deletado is None:
            return {"erro": "Produto não encontrado."}
        return {"mensagem": "Produto excluído definitivamente do estoque."}
    except Exception as e:
        conn.rollback()
        return {"erro": f"Falha ao deletar produto: {e}"}
    finally:
        cursor.close()
        conn.close()

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_conexao()
    cursor = conn.cursor()
    try:
        # Busca o mercado pelo email (o Swagger usa 'username' no formulário)
        cursor.execute("SELECT id, nome, senha FROM Mercados WHERE email = %s;", (form_data.username,))
        mercado = cursor.fetchone()

        # Bloqueia se não achar o email ou a senha não bater
        if not mercado or not verificar_senha(form_data.password, mercado[2]):
            raise HTTPException(status_code=400, detail="Email ou senha incorretos.")

        # Fabrica o crachá com validade de 24 horas
        dados_cracha = {
            "sub": str(mercado[0]), 
            "nome": mercado[1],
            "exp": datetime.now(timezone.utc) + timedelta(hours=24) 
        }
        token = jwt.encode(dados_cracha, SECRET_KEY, algorithm=ALGORITHM)

        return {"access_token": token, "token_type": "bearer"}
    finally:
        cursor.close()
        conn.close()