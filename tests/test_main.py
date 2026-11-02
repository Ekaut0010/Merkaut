from fastapi.testclient import TestClient
from uuid import uuid4
from main import app
from datetime import datetime, timedelta, timezone
import jwt
from app.config import SECRET_KEY, ALGORITHM

client = TestClient(app)


def test_raiz():
    response = client.get("/")

    assert response.status_code == 200

    dados = response.json()

    assert dados["mensagem"] == "O servidor do Merkaut está online!"
    assert dados["versao"] == "1.0.0"

def test_criar_mercado():
    email_teste = f"{uuid4().hex}@merkaut.com"

    response = client.post(
        "/mercados/",
        json={
            "nome": "Mercado Teste Pytest",
            "email": email_teste,
            "senha": "SenhaTeste123"
        }
    )

    assert response.status_code == 201

    dados = response.json()

    assert dados["nome"] == "Mercado Teste Pytest"
    assert dados["email"] == email_teste
    assert "senha" not in dados

def test_login():
    email_teste = f"{uuid4().hex}@merkaut.com"
    senha_teste = "SenhaTeste123"

    # Primeiro, cadastra o mercado
    cadastro = client.post(
        "/mercados/",
        json={
            "nome": "Mercado Login Teste",
            "email": email_teste,
            "senha": senha_teste
        }
    )

    assert cadastro.status_code == 201

    # Depois, tenta fazer login
    response = client.post(
        "/login",
        data={
            "username": email_teste,
            "password": senha_teste
        }
    )

    assert response.status_code == 200

    dados = response.json()

    assert "access_token" in dados
    assert dados["token_type"] == "bearer"

def test_isolamento_entre_mercados():
    # Criando dois mercados
    email_a = f"{uuid4().hex}@merkaut.com"
    email_b = f"{uuid4().hex}@merkaut.com"
    senha = "SenhaTeste123"

    for email, nome in [
        (email_a, "Mercado A"),
        (email_b, "Mercado B")
    ]:
        response = client.post(
            "/mercados/",
            json={
                "nome": nome,
                "email": email,
                "senha": senha
            }
        )
        assert response.status_code == 201

    # Fazendo login no Mercado A
    login_a = client.post(
        "/login",
        data={"username": email_a, "password": senha}
    )
    token_a = login_a.json()["access_token"]

    # Mercado A cadastra um produto
    produto = client.post(
        "/produtos/",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "nome": "Arroz Teste",
            "preco": 25.90,
            "codigo_de_barras": "123456789"
        }
    )
    assert produto.status_code == 201

    # Fazendo login no Mercado B
    login_b = client.post(
        "/login",
        data={"username": email_b, "password": senha}
    )
    token_b = login_b.json()["access_token"]

    # Mercado B tenta visualizar os produtos
    produtos_b = client.get(
        "/produtos/",
        headers={"Authorization": f"Bearer {token_b}"}
    )

    assert produtos_b.status_code == 200
    assert produtos_b.json() == []

def test_bloquear_alteracao_e_exclusao_de_outro_mercado():
    senha = "SenhaTeste123"
    email_a = f"{uuid4().hex}@merkaut.com"
    email_b = f"{uuid4().hex}@merkaut.com"

    # Criar os dois mercados
    for email, nome in [
        (email_a, "Mercado A"),
        (email_b, "Mercado B")
    ]:
        response = client.post(
            "/mercados/",
            json={
                "nome": nome,
                "email": email,
                "senha": senha
            }
        )
        assert response.status_code == 201

    # Login do Mercado A
    login_a = client.post(
        "/login",
        data={"username": email_a, "password": senha}
    )
    token_a = login_a.json()["access_token"]

    # Login do Mercado B
    login_b = client.post(
        "/login",
        data={"username": email_b, "password": senha}
    )
    token_b = login_b.json()["access_token"]

    # Mercado A cadastra um produto
    produto = client.post(
        "/produtos/",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "nome": "Produto Privado",
            "preco": 15.90,
            "codigo_de_barras": "987654321"
        }
    )
    assert produto.status_code == 201

    produto_id = produto.json()["id"]

    # Mercado B tenta alterar o produto de A
    alteracao = client.put(
        f"/produtos/{produto_id}",
        headers={"Authorization": f"Bearer {token_b}"},
        json={
            "nome": "Produto Invadido",
            "preco": 1.00,
            "codigo_de_barras": "111111111"
        }
    )
    assert alteracao.status_code == 404

    # Mercado B tenta excluir o produto de A
    exclusao = client.delete(
        f"/produtos/{produto_id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert exclusao.status_code == 404

def test_atualizar_e_excluir_produto_proprio():
    email = f"{uuid4().hex}@merkaut.com"
    senha = "SenhaTeste123"

    # Criar mercado
    cadastro = client.post(
        "/mercados/",
        json={
            "nome": "Mercado CRUD",
            "email": email,
            "senha": senha
        }
    )

    assert cadastro.status_code == 201

    # Fazer login
    login = client.post(
        "/login",
        data={
            "username": email,
            "password": senha
        }
    )

    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Cadastrar produto
    produto = client.post(
        "/produtos/",
        headers=headers,
        json={
            "nome": "Arroz",
            "preco": 25.90,
            "codigo_de_barras": "123456789"
        }
    )

    assert produto.status_code == 201

    produto_id = produto.json()["id"]

    # Atualizar produto
    atualizacao = client.put(
        f"/produtos/{produto_id}",
        headers=headers,
        json={
            "nome": "Arroz Integral",
            "preco": 29.90,
            "codigo_de_barras": "123456789"
        }
    )

    assert atualizacao.status_code == 200

    # Confirmar atualização
    consulta = client.get(
        "/produtos/",
        headers=headers
    )

    assert consulta.status_code == 200
    assert any(
        p["id"] == produto_id and p["nome"] == "Arroz Integral"
        for p in consulta.json()
    )

    # Excluir produto
    exclusao = client.delete(
        f"/produtos/{produto_id}",
        headers=headers
    )

    assert exclusao.status_code == 200

def test_bloquear_acesso_sem_token():
    # Tentar listar produtos sem autenticação
    response = client.get("/produtos/")

    assert response.status_code == 401

    # Tentar cadastrar produto sem autenticação
    response = client.post(
        "/produtos/",
        json={
            "nome": "Produto Não Autorizado",
            "preco": 10.00,
            "codigo_de_barras": "111222333"
        }
    )

    assert response.status_code == 401

def test_bloquear_token_invalido():
    headers = {
        "Authorization": "Bearer token_inventado_123"
    }

    response = client.get(
        "/produtos/",
        headers=headers
    )

    assert response.status_code == 401
    from datetime import datetime, timedelta, timezone
import jwt
from app.config import SECRET_KEY, ALGORITHM


def test_bloquear_token_expirado():
    token_expirado = jwt.encode(
        {
            "sub": "1",
            "nome": "Mercado Teste",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1)
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    headers = {
        "Authorization": f"Bearer {token_expirado}"
    }

    response = client.get(
        "/produtos/",
        headers=headers
    )

    assert response.status_code == 401

def test_bloquear_produto_com_dados_invalidos():
    email = f"{uuid4().hex}@merkaut.com"
    senha = "SenhaTeste123"

    cadastro = client.post(
        "/mercados/",
        json={
            "nome": "Mercado Validacao",
            "email": email,
            "senha": senha
        }
    )
    assert cadastro.status_code == 201

    login = client.post(
        "/login",
        data={"username": email, "password": senha}
    )
    token = login.json()["access_token"]

    response = client.post(
        "/produtos/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "nome": "A",
            "preco": -10,
            "codigo_de_barras": ""
        }
    )

    assert response.status_code == 422