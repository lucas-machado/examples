import { useContext } from "react";
import tasksContext from "./tasksContext";

const useTasks = () => useContext(tasksContext);

export default useTasks;
