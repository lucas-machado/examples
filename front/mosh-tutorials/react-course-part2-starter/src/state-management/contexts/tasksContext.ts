import React, { Dispatch } from "react";
import { Task, TaskAction } from "../reducers/taskReducer";

interface TasksContextType {
  tasks: Task[];
  dispatch: Dispatch<TaskAction>;
}

export default React.createContext<TasksContextType>({} as TasksContextType);
