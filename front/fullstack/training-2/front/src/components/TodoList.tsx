import { useRef } from "react";
import { useTodos, type Todo, type TodoCreateInput } from "../hooks/useTodos";
import { useForm, type FieldValues } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

const todoSchema = z.object({
  title: z
    .string()
    .min(4, { message: "title should be at least 4 characters" }),
  description: z.string().optional(),
});

type TodoFormData = z.infer<typeof todoSchema>;

export function TodoList() {
  const { todos, error, addTodo, deleteTodo } = useTodos();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<TodoFormData>({ resolver: zodResolver(todoSchema) });

  const onSubmit = async ({ title, description }: FieldValues) => {
    addTodo({ title, description });
    reset();
  };

  const handleDelete = (todo: Todo) => {
    deleteTodo(todo.id);
  };

  return (
    <>
      {error && <p>{error}</p>}
      <ul>
        {todos.map((todo) => (
          <li key={todo.id}>
            {todo.title} {todo.description}
            <button onClick={() => handleDelete(todo)}>Delete</button>
          </li>
        ))}
      </ul>
      <form onSubmit={handleSubmit(onSubmit)}>
        <label htmlFor="title">Nome</label>
        <input id="title" type="text" {...register("title")}></input>
        {errors.title && <p style={{ color: "red" }}>{errors.title.message}</p>}
        <label htmlFor="description">Descrição</label>
        <input
          id="description"
          type="text"
          {...register("description")}
        ></input>
        {errors.description && (
          <p style={{ color: "red" }}>{errors.description.message}</p>
        )}
        <button type="submit">Add</button>
      </form>
    </>
  );
}
