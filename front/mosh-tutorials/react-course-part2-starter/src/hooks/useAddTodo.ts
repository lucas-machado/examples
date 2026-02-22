import { useQueryClient, useMutation } from "@tanstack/react-query";
import { CACHE_KEY_TODOS } from "../react-query/constants";
import todoService, { Todo } from "../services/todoService";

export function useAddTodo(onOpStart: () => void) {
  const queryClient = useQueryClient();
  return useMutation<Todo, Error, Todo>({
    mutationFn: (todo: Todo) => todoService.post(todo),
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
