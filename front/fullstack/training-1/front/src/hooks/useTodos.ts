import { useState, useEffect } from "react";
import { AxiosError, CanceledError } from "axios";
import api from "../api/client";

export interface Todo {
  id: number;
  title: string;
  description?: string | null;
  completed: boolean;
}

export interface TodoCreateInput {
  title: string;
  description?: string;
}

export function useTodos() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    const fetchTodos = async () => {
      const request = api.get<Todo[]>("/todos", {
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

  const addTodo = async (input: TodoCreateInput) => {
    const newTodo: Todo = {
      id: Date.now() * -1,
      title: input.title,
      description: input.description,
      completed: false,
    };
    try {
      setTodos((curr) => [...curr, newTodo]);
      const response = await api.post<Todo>("/todos", input);
      setTodos((curr) =>
        curr.map((todo) => (todo.id === newTodo.id ? response.data : todo)),
      );
    } catch (err) {
      setError((err as AxiosError).message);
      setTodos((curr) => curr.filter((todo) => todo.id !== newTodo.id));
    }
  };

  const deleteTodo = async (id: number) => {
    const todoToRemove = todos.find((todo) => todo.id === id);
    if (!todoToRemove) return;

    try {
      setTodos((curr) => curr.filter((todo) => todo !== todoToRemove));
      await api.delete("/todos/" + id);
    } catch (err) {
      setError((err as AxiosError).message);
      setTodos((curr) => [...curr, todoToRemove]);
    }
  };

  return { todos, error, addTodo, deleteTodo };
}
