import { useRef } from "react";
import { useTodos, type Todo, type TodoCreateInput } from "../hooks/useTodos";

export function TodoList() {
  const { todos, error, addTodo, deleteTodo } = useTodos();
  const nameRef = useRef<HTMLInputElement>(null);
  const descriptionRef = useRef<HTMLInputElement>(null);

  const handleSubmit = (event: React.SubmitEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (nameRef.current) {
      addTodo({
        title: nameRef.current.value,
        description: descriptionRef.current?.value,
      });
      nameRef.current.value = "";
    }

    if (descriptionRef.current) descriptionRef.current.value = "";
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
      <form onSubmit={handleSubmit}>
        <label htmlFor="name">Nome</label>
        <input id="name" type="text" ref={nameRef}></input>
        <label htmlFor="description">Descrição</label>
        <input id="description" type="text" ref={descriptionRef}></input>
        <button type="submit">Add</button>
      </form>
    </>
  );
}
