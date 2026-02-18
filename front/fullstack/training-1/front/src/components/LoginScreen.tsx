import { useState } from "react";
import api from "../api/client";
import { AxiosError } from "axios";

interface LoginProps {
  onLogin: (token: string) => void;
}

export function LoginScreen({ onLogin }: LoginProps) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.SubmitEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError("");

    try {
      if (isLogin) {
        const res = await api.post(
          "/auth/login",
          new URLSearchParams({ username: email, password }),
          { headers: { "Content-Type": "application/x-www-form-urlencoded" } },
        );
        onLogin(res.data.access_token);
      } else {
        const res = await api.post("/auth/register", { email, password });
        onLogin(res.data.access_token);
      }
    } catch (err) {
      setError((err as AxiosError).message);
    }
  };

  return (
    <div>
      <h1>{isLogin ? "Entrar" : "Cadastrar"}</h1>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </label>

        <label>
          Senha
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>

        <button type="submit">{isLogin ? "Entrar" : "Cadastrar"}</button>
      </form>

      <button
        type="button"
        onClick={() => {
          setIsLogin(!isLogin);
          setError("");
        }}
      >
        {isLogin ? "Criar Conta" : "Já tenho conta"}
      </button>
    </div>
  );
}
