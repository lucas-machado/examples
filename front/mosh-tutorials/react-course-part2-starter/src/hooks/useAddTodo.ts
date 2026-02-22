import { useQueryClient, useMutation } from "@tanstack/react-query";
import { Todo } from "./useTodos";
import { CACHE_KEY_TODOS } from "../react-query/constants";
import APIClient from "../services/apiClient";

const apiClient = new APIClient<Todo>("/todos");

export function useAddTodo(onOpStart: () => void) {
  const queryClient = useQueryClient();
  return useMutation<Todo, Error, Todo>({
    mutationFn: (todo: Todo) => apiClient.post(todo),
    onMutate: (newTodo: Todo) => {
      queryClient.setQueryData<Todo[]>(CACHE_KEY_TODOS, (todos) => [
        newTodo,
        ...(todos || []),
      ]);

      onOpStart();
    },
    onSuccess: (savedTodo, newTodo) => {
      queryClient.setQueryData<Todo[]>(CACHE_KEY_TODOS, (todos) =>
        todos?.map((todo) => (todo === newTodo ? savedTodo : todo)),
      );
    },
    onError: (error, newTodo, context) => {
      queryClient.setQueryData<Todo[]>(
        CACHE_KEY_TODOS,
        (current) => current?.filter((todo) => todo !== newTodo) ?? [],
      );
    },
  });
}
