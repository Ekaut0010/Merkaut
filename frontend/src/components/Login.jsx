import { useState } from "react";
import API_URL from "../api";
import "./Login.css";

function Login({ onLoginSuccess }) {
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [erro, setErro] = useState("");
  const [carregando, setCarregando] = useState(false);

  async function fazerLogin(evento) {
    evento.preventDefault();

    setErro("");
    setCarregando(true);

    try {
      const dados = new URLSearchParams();

      dados.append("username", email);
      dados.append("password", senha);

      const resposta = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: dados,
      });

      const resultado = await resposta.json();

      if (!resposta.ok) {
        throw new Error("E-mail ou senha incorretos.");
      }

      localStorage.setItem("token", resultado.access_token);

      onLoginSuccess();
    } catch (erro) {
      setErro(erro.message || "Não foi possível conectar ao servidor.");
    } finally {
      setCarregando(false);
    }
  }
  return (
    <div className="login-container">
      <div className="login-card">
        <h1 className="login-logo">
          merkaut<span>.</span>
        </h1>

        <div className="login-header">
          <h2>Bem-vindo de volta</h2>
          <p>Entre na sua conta para continuar.</p>
        </div>

        <form className="login-form" onSubmit={fazerLogin}>
          <div className="form-group">
            <label htmlFor="email">E-mail</label>
            <input
              type="email"
              id="email"
              placeholder="seu@email.com"
              value={email}
              onChange={(evento) => setEmail(evento.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="senha">Senha</label>
            <input
              type="password"
              id="senha"
              placeholder="Digite sua senha"
              value={senha}
              onChange={(evento) => setSenha(evento.target.value)}
              required
            />
          </div>
          {erro && <p className="login-error">{erro}</p>}
          <button type="submit" disabled={carregando}>
            {carregando ? "Entrando..." : "Entrar"}
          </button>
        </form>

        <p className="login-footer">Gestão inteligente para o seu mercado.</p>
      </div>
    </div>
  );
}

export default Login;
