import { useContext } from "react";
import tasksContext from "../contexts/tasksContext";

const useTasks = () => useContext(tasksContext);

export default useTasks;
