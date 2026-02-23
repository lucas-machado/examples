import { ReactNode, useReducer } from "react";
import taskReducer from "./taskReducer";
import TasksContext from "./tasksContext";

interface Props {
  children: ReactNode;
}

export default function TaskProvider({ children }: Props) {
  const [tasks, dispatch] = useReducer(taskReducer, []);

  return (
    <TasksContext.Provider value={{ tasks, dispatch }}>
      {children}
    </TasksContext.Provider>
  );
}
