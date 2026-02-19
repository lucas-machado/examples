import { useState } from "react";
import api from "../api/client";
import { AxiosError } from "axios";
import { useForm, type FieldValues } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

const loginSchema = z.object({
  email: z.email({ message: "invalid email " }),
  password: z
    .string()
    .min(2, { message: "password needs to have at least 2 characters " }),
});

type LoginFormData = z.infer<typeof loginSchema>;

interface LoginProps {
  onLogin: (token: string) => void;
}

export function LoginScreen({ onLogin }: LoginProps) {
  const [isLogin, setIsLogin] = useState(true);
  const [error, setError] = useState("");

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({ resolver: zodResolver(loginSchema) });

  const onSubmit = async ({ email, password }: FieldValues) => {
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
      <form onSubmit={handleSubmit(onSubmit)}>
        <label>
          Email
          <input type="email" {...register("email")} />
        </label>
        {errors.email && <p style={{ color: "red" }}>{errors.email.message}</p>}

        <label>
          Senha
          <input type="password" {...register("password")} />
        </label>
        {errors.password && (
          <p style={{ color: "red" }}>{errors.password.message}</p>
        )}

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
