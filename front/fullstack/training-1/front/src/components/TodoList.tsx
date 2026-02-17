import { useRef } from "react";
import { useTodos, type Todo } from "../hooks/useTodos";

export function TodoList() {
  const { todos, error, addTodo } = useTodos();
  const nameRef = useRef<HTMLInputElement>(null);

  const handleSubmit = () => {
    if (nameRef.current) addTodo(nameRef.current.value);
  };

  return (
    <>
      {error && <p>{error}</p>}
      <ul>
        {todos.map((todo) => (
          <li key={todo.id}>{todo.name}</li>
        ))}
      </ul>
      <form onSubmit={handleSubmit}>
        <label htmlFor="name">Nome</label>
        <input id="name" type="text" ref={nameRef}></input>
        <button>Add</button>
      </form>
    </>
  );
}
