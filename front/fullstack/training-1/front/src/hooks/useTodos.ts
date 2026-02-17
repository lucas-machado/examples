import { useState, useEffect } from "react";
import axios, { AxiosError, CanceledError } from "axios";

export interface Todo {
  id: number;
  name: string;
}

export function useTodos() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    const fetchTodos = async () => {
      const request = axios.get<Todo[]>("http://localhost:8000/todo", {
        signal: controller.signal,
      });

      try {
        const response = await request;
        setTodos(response.data);
      } catch (err) {
        if (err instanceof CanceledError) return;
        setError((err as AxiosError).message);
      }
    };

    fetchTodos();

    return () => controller.abort();
  }, []);

  const addTodo = async (name: string) => {
    const newTodo = { id: Date.now() * -1, name: name };
    try {
      setTodos((curr) => [...curr, newTodo]);
      const response = await axios.post<Todo>("http://localhost:8000/todo", {
        name,
      });
      setTodos((curr) =>
        curr.map((todo) => (todo === newTodo ? response.data : todo)),
      );
    } catch (err) {
      setError((err as AxiosError).message);
      setTodos((curr) => curr.filter((todo) => todo !== newTodo));
    }
  };

  return { todos, error, addTodo };
}
