import { useState } from "react";
import Login from "./components/Login";
import "./App.css";

function App() {
  const [temaEscuro, setTemaEscuro] = useState(false);
  const [modalAberto, setModalAberto] = useState(false);
  const [autenticado, setAutenticado] = useState(() =>
    Boolean(localStorage.getItem("token")),
  );

  const [novoProduto, setNovoProduto] = useState({
    nome: "",
    preco: "",
    codigo_de_barras: "",
    quantidade_estoque: 0,
    estoque_minimo: 5,
  });

  function alternarTema() {
    setTemaEscuro((temaAtual) => !temaAtual);
  }

  function cadastrarProduto(evento) {
    evento.preventDefault();

    const produto = {
      nome: novoProduto.nome.trim(),
      preco: Number(novoProduto.preco),
      codigo_de_barras: novoProduto.codigo_de_barras.trim(),
      quantidade_estoque: Number(novoProduto.quantidade_estoque),
      estoque_minimo: Number(novoProduto.estoque_minimo),
    };

    if (produto.nome.length < 2 || produto.nome.length > 150) {
      alert("O nome deve ter entre 2 e 150 caracteres.");
      return;
    }

    if (!Number.isFinite(produto.preco) || produto.preco <= 0) {
      alert("Informe um preço maior que zero.");
      return;
    }

    if (
      produto.codigo_de_barras.length < 1 ||
      produto.codigo_de_barras.length > 50
    ) {
      alert("Informe um código de barras válido.");
      return;
    }

    if (
      !Number.isInteger(produto.quantidade_estoque) ||
      produto.quantidade_estoque < 0
    ) {
      alert("A quantidade deve ser um número inteiro igual ou maior que zero.");
      return;
    }

    if (
      !Number.isInteger(produto.estoque_minimo) ||
      produto.estoque_minimo < 0
    ) {
      alert(
        "O estoque mínimo deve ser um número inteiro igual ou maior que zero.",
      );
      return;
    }

    console.log("Produto validado:", produto);
  }

  return (
    <div className={`app ${temaEscuro ? "dark" : "light"}`}>
      {!autenticado ? (
        <Login onLoginSuccess={() => setAutenticado(true)} />
      ) : (
        <>
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

          <main className="main-content">
            <header className="topbar">
              <div>
                <p className="breadcrumb">Visão geral / Dashboard</p>
                <h2>Dashboard</h2>
              </div>

              <div className="user-actions">
                <button
                  type="button"
                  className="theme-toggle"
                  onClick={alternarTema}
                  aria-label="Alternar tema"
                >
                  {temaEscuro ? "☀️" : "🌙"}
                </button>

                <div className="user-profile">
                  <div className="avatar">C</div>
                  <span>Meu Mercado</span>
                </div>
              </div>
            </header>

            <section className="welcome">
              <h2>Bem-vindo ao Merkaut 👋</h2>
              <p>Gerencie seu mercado de forma simples e inteligente.</p>
            </section>

            <section className="stats">
              <div className="stat-card">
                <p>Total de produtos</p>
                <h3>0</h3>
                <span>Produtos cadastrados</span>
              </div>

              <div className="stat-card">
                <p>Estoque baixo</p>
                <h3>0</h3>
                <span>Precisam de reposição</span>
              </div>

              <div className="stat-card">
                <p>Valor em estoque</p>
                <h3>R$ 0,00</h3>
                <span>Valor total estimado</span>
              </div>
            </section>

            <section className="products-section">
              <div>
                <h3>Produtos recentes</h3>
                <p>Seus produtos aparecerão aqui.</p>
              </div>

              <button type="button" onClick={() => setModalAberto(true)}>
                + Novo produto
              </button>
            </section>

            {modalAberto && (
              <div className="modal-overlay">
                <div className="modal">
                  <div className="modal-header">
                    <h2>Novo produto</h2>

                    <button type="button" onClick={() => setModalAberto(false)}>
                      ✕
                    </button>
                  </div>

                  <p>Preencha as informações do produto.</p>

                  <form className="product-form" onSubmit={cadastrarProduto}>
                    <div className="form-group">
                      <label htmlFor="nome">Nome do produto</label>
                      <input
                        type="text"
                        id="nome"
                        placeholder="Ex: Arroz 5kg"
                        value={novoProduto.nome}
                        onChange={(evento) =>
                          setNovoProduto({
                            ...novoProduto,
                            nome: evento.target.value,
                          })
                        }
                      />
                    </div>

                    <div className="form-group">
                      <label htmlFor="preco">Preço</label>
                      <input
                        type="number"
                        id="preco"
                        placeholder="0.00"
                        step="0.01"
                        min="0"
                        value={novoProduto.preco}
                        onChange={(evento) =>
                          setNovoProduto({
                            ...novoProduto,
                            preco: evento.target.value,
                          })
                        }
                      />
                    </div>

                    <div className="form-group">
                      <label htmlFor="codigo">Código de barras</label>
                      <input
                        type="text"
                        id="codigo"
                        placeholder="Digite o código de barras"
                        value={novoProduto.codigo_de_barras}
                        onChange={(evento) =>
                          setNovoProduto({
                            ...novoProduto,
                            codigo_de_barras: evento.target.value,
                          })
                        }
                      />
                    </div>

                    <div className="form-group">
                      <label htmlFor="quantidade">Quantidade em estoque</label>
                      <input
                        type="number"
                        id="quantidade"
                        placeholder="0"
                        min="0"
                        value={novoProduto.quantidade_estoque}
                        onChange={(evento) =>
                          setNovoProduto({
                            ...novoProduto,
                            quantidade_estoque: evento.target.value,
                          })
                        }
                      />
                    </div>

                    <div className="form-group">
                      <label htmlFor="estoqueMinimo">Estoque mínimo</label>
                      <input
                        type="number"
                        id="estoqueMinimo"
                        placeholder="5"
                        min="0"
                        value={novoProduto.estoque_minimo}
                        onChange={(evento) =>
                          setNovoProduto({
                            ...novoProduto,
                            estoque_minimo: evento.target.value,
                          })
                        }
                      />
                    </div>

                    <div className="form-actions">
                      <button
                        type="button"
                        onClick={() => setModalAberto(false)}
                      >
                        Cancelar
                      </button>

                      <button type="submit">Cadastrar produto</button>
                    </div>
                  </form>
                </div>
              </div>
            )}
          </main>
        </>
      )}
    </div>
  );
}

export default App;
