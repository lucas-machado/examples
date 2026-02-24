import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import z from "zod";
import axiosInstance from "./core/axiosInstance";
import type { AxiosError } from "axios";
import { useAuthStore } from "./auth/useAuthStore";
import { useNavigate } from "react-router-dom";

const loginSchema = z.object({
  email: z.email({ message: "invalid email" }),
  password: z.string().min(2, "password needs to have at least 2 characters"),
});

type LoginFormData = z.infer<typeof loginSchema>;

const LoginPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [error, setError] = useState("");

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({ resolver: zodResolver(loginSchema) });

  const navigate = useNavigate();

  const onSubmit = async ({ email, password }: LoginFormData) => {
    try {
      if (isLogin) {
        const res = await axiosInstance.post(
          "/auth/login",
          new URLSearchParams({ username: email, password }),
          { headers: { "Content-Type": "application/x-www-form-urlencoded" } },
        );

        useAuthStore.getState().setToken(res.data.access_token);
        navigate("/moments", { replace: true });
      } else {
        const res = await axiosInstance.post("/auth/register", {
          email,
          password,
        });

        useAuthStore.getState().setToken(res.data.access_token);
        navigate("/moments", { replace: true });
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
};

export default LoginPage;
