import { useEffect, useState } from "react";

import API_URL from "./api";
import Login from "./components/Login";
import "./App.css";

// CONFIGURAÇÕES

const CATEGORIAS = [
  "Hortifruti",
  "Açougue",
  "Limpeza",
  "Higiene",
  "Beleza",
  "Eletrônicos",
  "Diversos",
];

const UNIDADES = [
  { valor: "UN", nome: "Unidade (UN)" },
  { valor: "KG", nome: "Quilograma (KG)" },
  { valor: "G", nome: "Grama (G)" },
  { valor: "L", nome: "Litro (L)" },
  { valor: "M", nome: "Metro (M)" },
];

function criarProdutoInicial() {
  return {
    nome: "",
    preco: "",
    codigo_de_barras: "",
    quantidade_estoque: 0,
    estoque_minimo: 5,
    categoria: "Diversos",
    unidade_medida: "UN",
  };
}

function formatarMoeda(valor) {
  return Number(valor || 0).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });
}
function formatarQuantidade(valor) {
  return Number(valor || 0).toLocaleString("pt-BR", {
    minimumFractionDigits: 3,
    maximumFractionDigits: 3,
  });
}

// COMPONENTE PRINCIPAL

function App() {
  // ESTADOS

  const [temaEscuro, setTemaEscuro] = useState(false);
  const [autenticado, setAutenticado] = useState(() =>
    Boolean(localStorage.getItem("token")),
  );

  const [produtos, setProdutos] = useState([]);
  const [carregandoProdutos, setCarregandoProdutos] = useState(true);
  const [erroProdutos, setErroProdutos] = useState("");

  const [modalAberto, setModalAberto] = useState(false);
  const [salvandoProduto, setSalvandoProduto] = useState(false);

  const [novoProduto, setNovoProduto] = useState(criarProdutoInicial);
  const [produtoEditando, setProdutoEditando] = useState(null);

  // CARREGAR PRODUTOS

  useEffect(() => {
    if (!autenticado) {
      setProdutos([]);
      setCarregandoProdutos(false);
      return;
    }

    const controlador = new AbortController();

    async function carregarProdutos() {
      setCarregandoProdutos(true);
      setErroProdutos("");

      const token = localStorage.getItem("token");

      try {
        const resposta = await fetch(`${API_URL}/produtos/`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
          signal: controlador.signal,
        });

        if (!resposta.ok) {
          throw new Error("Não foi possível carregar os produtos.");
        }

        const dados = await resposta.json();

        setProdutos(dados);
      } catch (erro) {
        if (erro.name !== "AbortError") {
          console.error(erro);
          setErroProdutos(erro.message);
        }
      } finally {
        if (!controlador.signal.aborted) {
          setCarregandoProdutos(false);
        }
      }
    }

    carregarProdutos();

    return () => controlador.abort();
  }, [autenticado]);

  // ATUALIZAR CAMPOS DO FORMULÁRIO

  function atualizarCampo(evento) {
    const { name, value } = evento.target;

    setNovoProduto((produtoAtual) => ({
      ...produtoAtual,
      [name]: value,
    }));
  }

  // FECHAR MODAL

  function fecharModal() {
    setModalAberto(false);
    setProdutoEditando(null);
    setNovoProduto(criarProdutoInicial());
  }

  // CADASTRAR PRODUTO

  async function cadastrarProduto(evento) {
    evento.preventDefault();

    if (salvandoProduto) return;

    const produto = {
      nome: novoProduto.nome.trim(),
      preco: Number(novoProduto.preco),
      codigo_de_barras: novoProduto.codigo_de_barras.trim() || null,
      quantidade_estoque: Number(novoProduto.quantidade_estoque),
      estoque_minimo: Number(novoProduto.estoque_minimo),
      categoria: novoProduto.categoria,
      unidade_medida: novoProduto.unidade_medida,
    };

    // VALIDAÇÕES

    if (produto.nome.length < 2 || produto.nome.length > 150) {
      alert("O nome deve ter entre 2 e 150 caracteres.");
      return;
    }

    if (!Number.isFinite(produto.preco) || produto.preco <= 0) {
      alert("Informe um preço maior que zero.");
      return;
    }

    if (
      produto.codigo_de_barras !== null &&
      produto.codigo_de_barras.length > 50
    ) {
      alert("O código de barras deve ter no máximo 50 caracteres.");
      return;
    }

    if (
      !Number.isFinite(produto.quantidade_estoque) ||
      produto.quantidade_estoque < 0
    ) {
      alert("A quantidade deve ser um número válido igual ou maior que zero.");
      return;
    }

    if (
      !Number.isFinite(produto.estoque_minimo) ||
      produto.estoque_minimo < 0
    ) {
      alert(
        "O estoque mínimo deve ser um número válido igual ou maior que zero.",
      );
      return;
    }

    // ENVIO PARA A API

    const token = localStorage.getItem("token");

    setSalvandoProduto(true);

    try {
      const resposta = await fetch(`${API_URL}/produtos/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(produto),
      });

      if (!resposta.ok) {
        const erro = await resposta.json();

        throw new Error(
          typeof erro.detail === "string"
            ? erro.detail
            : "Não foi possível cadastrar o produto.",
        );
      }

      const dados = await resposta.json();

      // ATUALIZA A LISTA SEM RECARREGAR A PÁGINA

      setProdutos((produtosAtuais) => [
        {
          ...produto,
          id: dados.id,
        },
        ...produtosAtuais,
      ]);

      alert("Produto cadastrado com sucesso!");

      fecharModal();
    } catch (erro) {
      alert(erro.message);
      console.error(erro);
    } finally {
      setSalvandoProduto(false);
    }
  }

  // ENCERRAR SESSÃO

  function sair() {
    localStorage.removeItem("token");
    setAutenticado(false);
    setModalAberto(false);
  }

  // INDICADORES DO DASHBOARD

  const totalProdutos = produtos.length;

  const produtosBaixoEstoque = produtos.filter(
    (produto) =>
      Number(produto.quantidade_estoque) <= Number(produto.estoque_minimo),
  ).length;

  const valorTotalEstoque = produtos.reduce(
    (total, produto) =>
      total + Number(produto.preco) * Number(produto.quantidade_estoque),
    0,
  );

  // TELA DE LOGIN

  if (!autenticado) {
    return (
      <div className="app light">
        <Login onLoginSuccess={() => setAutenticado(true)} />
      </div>
    );
  }

  // DASHBOARD

  return (
    <div className={`app ${temaEscuro ? "dark" : "light"}`}>
      {/* MENU LATERAL */}

      <aside className="sidebar">
        <h1 className="logo">
          merkaut<span>.</span>
        </h1>

        <nav>
          <p className="menu-label">MENU PRINCIPAL</p>

          <a href="#" className="nav-link active">
            <span>▦</span>
            Dashboard
          </a>

          <a href="#" className="nav-link">
            <span>📦</span>
            Produtos
          </a>

          <a href="#" className="nav-link">
            <span>📊</span>
            Estoque
          </a>
        </nav>

        <div className="sidebar-footer">
          <p>MERKAUT</p>
          <span>Gestão inteligente</span>
        </div>
      </aside>

      {/* CONTEÚDO PRINCIPAL */}

      <main className="main-content">
        {/* CABEÇALHO */}

        <header className="topbar">
          <div>
            <p className="breadcrumb">Visão geral / Dashboard</p>

            <h2>Dashboard</h2>
          </div>

          <div className="user-actions">
            <button
              type="button"
              className="theme-toggle"
              onClick={() => setTemaEscuro((atual) => !atual)}
              aria-label="Alternar tema"
            >
              {temaEscuro ? "☀️" : "🌙"}
            </button>

            <div className="user-profile">
              <div className="avatar">C</div>
              <span>Meu Mercado</span>
            </div>

            <button type="button" className="logout-button" onClick={sair}>
              Sair
            </button>
          </div>
        </header>

        {/* BOAS-VINDAS */}

        <section className="welcome">
          <h2>Bem-vindo ao Merkaut 👋</h2>
          <p>Gerencie seu mercado de forma simples e inteligente.</p>
        </section>

        {/* INDICADORES */}

        <section className="stats">
          <div className="stat-card">
            <p>Total de produtos</p>
            <h3>{totalProdutos}</h3>
            <span>Produtos cadastrados</span>
          </div>

          <div className="stat-card">
            <p>Estoque baixo</p>
            <h3>{produtosBaixoEstoque}</h3>
            <span>Precisam de reposição</span>
          </div>

          <div className="stat-card">
            <p>Valor em estoque</p>
            <h3>{formatarMoeda(valorTotalEstoque)}</h3>
            <span>Valor total estimado</span>
          </div>
        </section>

        {/* PRODUTOS RECENTES */}

        <section className="products-section">
          <div>
            <h3>Produtos recentes</h3>
            <p>Seus produtos cadastrados no Merkaut.</p>
          </div>

          <button type="button" onClick={() => setModalAberto(true)}>
            + Novo produto
          </button>

          <div className="products-list">
            {carregandoProdutos ? (
              <p>Carregando produtos...</p>
            ) : erroProdutos ? (
              <p>{erroProdutos}</p>
            ) : produtos.length === 0 ? (
              <p>Nenhum produto cadastrado.</p>
            ) : (
              produtos.map((produto) => {
                const estoqueBaixo =
                  Number(produto.quantidade_estoque) <=
                  Number(produto.estoque_minimo);
                const semEstoque = Number(produto.quantidade_estoque) === 0;

                return (
                  <div className="product-item" key={produto.id}>
                    <div>
                      <strong>{produto.nome}</strong>

                      <p>
                        Código: {produto.codigo_de_barras || "Não informado"}
                      </p>

                      <p>
                        {produto.categoria} · {produto.unidade_medida}
                      </p>
                    </div>

                    <div>
                      <strong>{formatarMoeda(produto.preco)}</strong>
                      {semEstoque ? (
                        <span className="stock-empty-alert">Sem estoque</span>
                      ) : estoqueBaixo ? (
                        <span className="stock-alert">Estoque baixo</span>
                      ) : null}

                      <p>
                        Estoque:{" "}
                        {formatarQuantidade(produto.quantidade_estoque)}{" "}
                        {produto.unidade_medida}
                      </p>
                      <p>
                        Estoque mínimo:{" "}
                        {formatarQuantidade(produto.estoque_minimo)}{" "}
                        {produto.unidade_medida}
                      </p>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </section>

        {/* MODAL DE CADASTRO */}

        {modalAberto && (
          <div className="modal-overlay">
            <div className="modal">
              <div className="modal-header">
                <h2>Novo produto</h2>

                <button type="button" onClick={fecharModal}>
                  ✕
                </button>
              </div>

              <p>Preencha as informações do produto.</p>

              <form className="product-form" onSubmit={cadastrarProduto}>
                {/* NOME */}

                <div className="form-group">
                  <label htmlFor="nome">Nome do produto</label>

                  <input
                    type="text"
                    id="nome"
                    name="nome"
                    placeholder="Ex: Arroz 5kg"
                    value={novoProduto.nome}
                    onChange={atualizarCampo}
                    minLength={2}
                    maxLength={150}
                    required
                  />
                </div>

                {/* PREÇO */}

                <div className="form-group">
                  <label htmlFor="preco">Preço</label>

                  <input
                    type="number"
                    id="preco"
                    name="preco"
                    placeholder="0.00"
                    step="0.01"
                    min="0.01"
                    value={novoProduto.preco}
                    onChange={atualizarCampo}
                    required
                  />
                </div>

                {/* CÓDIGO DE BARRAS */}

                <div className="form-group">
                  <label htmlFor="codigo">Código de barras (opcional)</label>

                  <input
                    type="text"
                    id="codigo"
                    name="codigo_de_barras"
                    placeholder="Digite o código de barras"
                    value={novoProduto.codigo_de_barras}
                    onChange={atualizarCampo}
                    maxLength={50}
                  />
                </div>

                {/* QUANTIDADE */}

                <div className="form-group">
                  <label htmlFor="quantidade">Quantidade em estoque</label>

                  <input
                    type="number"
                    id="quantidade"
                    name="quantidade_estoque"
                    placeholder="0"
                    min="0"
                    step="0.001"
                    value={novoProduto.quantidade_estoque}
                    onChange={atualizarCampo}
                    required
                  />
                </div>

                {/* ESTOQUE MÍNIMO */}

                <div className="form-group">
                  <label htmlFor="estoqueMinimo">Estoque mínimo</label>

                  <input
                    type="number"
                    id="estoqueMinimo"
                    name="estoque_minimo"
                    placeholder="5"
                    min="0"
                    step="0.001"
                    value={novoProduto.estoque_minimo}
                    onChange={atualizarCampo}
                    required
                  />
                </div>

                {/* CATEGORIA */}

                <div className="form-group">
                  <label htmlFor="categoria">Categoria</label>

                  <select
                    id="categoria"
                    name="categoria"
                    value={novoProduto.categoria}
                    onChange={atualizarCampo}
                  >
                    {CATEGORIAS.map((categoria) => (
                      <option key={categoria} value={categoria}>
                        {categoria}
                      </option>
                    ))}
                  </select>
                </div>

                {/* UNIDADE DE MEDIDA */}

                <div className="form-group">
                  <label htmlFor="unidade_medida">Unidade de medida</label>

                  <select
                    id="unidade_medida"
                    name="unidade_medida"
                    value={novoProduto.unidade_medida}
                    onChange={atualizarCampo}
                  >
                    {UNIDADES.map((unidade) => (
                      <option key={unidade.valor} value={unidade.valor}>
                        {unidade.nome}
                      </option>
                    ))}
                  </select>
                </div>

                {/* AÇÕES */}

                <div className="form-actions">
                  <button
                    type="button"
                    onClick={fecharModal}
                    disabled={salvandoProduto}
                  >
                    Cancelar
                  </button>

                  <button type="submit" disabled={salvandoProduto}>
                    {salvandoProduto ? "Cadastrando..." : "Cadastrar produto"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
